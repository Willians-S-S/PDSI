// Função para fazer a requisição à API
function carregarDadosDaAPI() {
    const urlParams = new URLSearchParams(window.location.search);
    const animalId = urlParams.get('id'); 
    const URL = `http://localhost:8000/animal/${animalId}`;
    const token = localStorage.getItem('token');

    // if (!token) {
    //   alert('Você precisa estar logado para acessar esta página.');
    //   window.location.href = 'login.html'; 
    // }

    fetch(URL,{ 
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }})
        .then(response => {
            if (response.status == 401){
                alert('Você precisa estar logado para acessar esta página.');
                window.location.href = 'login.html'; 
            }
            if (!response.ok) {
                throw new Error(`Erro na requisição: ${response.status}`);
            }
            console.log(response);
            return response.json();
        })
        .then(data => {
            const URL_IMAGE = `http://127.0.0.1:8000/images/${data.image_url}` 

            fetch(URL_IMAGE)
                .then(response => {
                    const contentType = response.headers.get("content-type") || "";
                    if (!response.ok || !contentType.includes("image")) {
                        console.warn("Imagem não encontrada ou formato inválido. Usando imagem padrão.");
                        throw new Error("Imagem não encontrada");
                    }
                    return response.blob();
                })
                .then(imageBlob => {
                    console.log(imageBlob);
                    if (imageBlob.size === 0) {
                        console.warn("A imagem está vazia. Usando imagem padrão.");
                        throw new Error("Imagem vazia ou inválida");
                    }

                    let image = window.URL.createObjectURL(imageBlob);
                    exibirDadosNaPagina(data, image);
                })
                .catch(error => {
                    console.error("Erro ao carregar a imagem:", error);
                });
        })
        .catch(error => {
            alert('Você precisa estar logado para acessar esta página.');
            window.location.href = 'login.html';
        });
}

function exibirDadosNaPagina(data, image) {
    console.log(data);
    const animal = data;

    document.getElementById("name-animal").innerText = `Identificação: ${animal.name || "Não informado"}`;
    document.getElementById("profile-image-animal").src = image;

    const infoList = document.getElementById("animal-ul");

    infoList.innerHTML = `
                <li><strong>Raça:</strong> ${animal.breed || "Não informado"}</li>
                <li><strong>Idade:</strong> ${animal.age !== null ? animal.age + " anos" : "Não informado"}</li>
                <li><strong>Gênero:</strong> ${animal.gender || "Não informado"}</li>
                <li><strong>Condição de Saúde:</strong> ${animal.health_condition || "Não informado"}</li>
                <li><strong>Peso Atual:</strong> ${animal.current_weight !== null ? animal.current_weight.toFixed(2) + " kg" : "Não informado"}</li>
                <li><strong>Data de Criação:</strong> ${animal.created_at ? new Date(animal.created_at).toLocaleDateString() : "Não informado"}</li>
                <li><strong>Última Atualização:</strong> ${animal.updated_at ? new Date(animal.updated_at).toLocaleDateString() : "Não informado"}</li>
            `;

    let pesos = "";
    
    
    animal.historys.forEach(element => {
        pesos += `<li>Peso Predito: ${element.current_weight.toFixed(2)} kg, Peso Manual: ${element.weight_manual !== null ? element.weight_manual.toFixed(2) + " kg" : "Não informado"}, Data: ${new Date(element.created_at).toLocaleDateString()}</li>`;
    });
    
    document.getElementById("historico-peso").innerHTML = pesos;
    
}

document.getElementById("editar-animal").addEventListener("click", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const animalId = urlParams.get('id'); 

    if (!animalId) {
        console.error("ID do animal não encontrado na URL.");
        return; 
    }

    window.location.href = `atualizar-animal.html?id=${animalId}`;
});

document.getElementById("nova-avaliacao").addEventListener("click", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const animalId = urlParams.get('id'); 

    if (!animalId) {
        console.error("ID do animal não encontrado na URL.");
        return; 
    }

    window.location.href = `inferencia.html?id=${animalId}`;
});


document.getElementById("excluir-animal").addEventListener("click", () => {
    // --- 1. Melhorar a confirmação para o usuário ---
    const animalName = document.getElementById("name-animal").innerText.replace("Identificação: ", "").trim();
    const confirmMessage = `Você tem certeza que deseja excluir o animal "${animalName}"? \n\nEsta ação é irreversível e todo o seu histórico será perdido.`;
    
    if (!confirm(confirmMessage)) {
        console.log("Exclusão cancelada pelo usuário.");
        return; // Interrompe a função se o usuário clicar em "Cancelar"
    }

    // --- 2. Obter os dados necessários (ID e Token) ---
    const urlParams = new URLSearchParams(window.location.search);
    const animalId = urlParams.get('id');
    const token = localStorage.getItem('token');

    // Validação de segurança
    if (!animalId) {
        alert("Erro: ID do animal não encontrado na URL. Não é possível excluir.");
        console.error("ID do animal não encontrado na URL.");
        return;
    }

    if (!token) {
        alert("Erro: Token de autenticação não encontrado. Por favor, faça o login novamente.");
        window.location.href = 'login.html';
        return;
    }

    const URL = `http://localhost:8000/animal/${animalId}`;

    // --- 3. Fazer a requisição FETCH com a lógica correta ---
    fetch(URL, {
        method: 'DELETE',
        headers: {
            // **CORREÇÃO CRÍTICA**: O cabeçalho de autorização é essencial
            // para que a sua API (get_current_user) identifique o usuário.
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        // A rota retorna 204 (No Content) em caso de sucesso.
        // A propriedade 'ok' do response cobre status de 200 a 299.
        if (response.ok) {
            return; // Sucesso, não há corpo na resposta para processar.
        }
        
        // Se a resposta não for 'ok', tratamos os erros mais comuns.
        if (response.status === 401) {
            throw new Error("Não autorizado. Sua sessão pode ter expirado.");
        }
        if (response.status === 404) {
            throw new Error("Animal não encontrado. Talvez já tenha sido excluído.");
        }
        // Para outros erros (ex: 500, 403)
        throw new Error(`O servidor respondeu com um erro: ${response.status}`);
    })
    .then(() => {
        // Este bloco só é executado se a resposta foi 'ok' (sucesso).
        alert(`Animal "${animalName}" foi excluído com sucesso!`);
        // window.history.back() é uma boa opção para voltar à tela anterior (ex: lista de animais).
        window.history.back();
    })
    .catch(error => {
        // Este 'catch' captura qualquer erro lançado nos blocos '.then' ou erros de rede.
        console.error("Erro ao tentar excluir o animal:", error);
        alert(`Falha ao excluir o animal. Motivo: ${error.message}`);
    });
});

window.addEventListener('load', carregarDadosDaAPI);
