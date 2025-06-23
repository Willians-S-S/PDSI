function carregarDadosDaFazenda() {   
    const urlParams = new URLSearchParams(window.location.search);
    const farmId = urlParams.get('id'); 

    const URL = `http://127.0.0.1:8000/farm/${farmId}`;

    if (farmId) {
        fetch(URL)
            .then(response => response.json())
            .then(data => {
                console.log("Dados da fazenda:", data);
                exibirDadosNaPagina(data);
                carregarImagensDosAnimais(data.animals);
            })
            .catch(error => {
                console.error("Erro ao buscar detalhes da fazenda:", error);
            });
    } else {
        console.error("ID da fazenda não encontrado na URL.");
    }
}

function carregarImagensDosAnimais(animais) {
    console.log(animais[0].image_url);
    animais.forEach(animal => {
        console.log(animal);
        if (animal.image_url) {
            console.log(animal.image_url);
            const URL_IMAGE = `http://127.0.0.1:8000/images/${animal.image_url}`;

            fetch(URL_IMAGE)
                .then(response => {
                    const contentType = response.headers.get("content-type") || "";
                    if (!response.ok || !contentType.includes("image")) {
                        console.warn(`Imagem do animal ${animal.name} não encontrada ou formato inválido. Usando imagem padrão.`);
                        throw new Error("Imagem não encontrada");
                    }
                    return response.blob();
                })
                .then(imageBlob => {
                    if (imageBlob.size === 0) {
                        console.warn(`A imagem do animal ${animal.name} está vazia. Usando imagem padrão.`);
                        throw new Error("Imagem vazia ou inválida");
                    }
                    console.log(imageBlob);
                    let imageUrl = window.URL.createObjectURL(imageBlob);
                    atualizarImagemDoAnimal(animal.id, imageUrl);
                })
                .catch(error => {
                    console.error(`Erro ao carregar a imagem do animal ${animal.name}:`, error);
                    atualizarImagemDoAnimal(animal.id, "caminho/para/imagem_padrao.jpg");
                });
        } else {
            atualizarImagemDoAnimal(animal.id, "caminho/para/imagem_padrao.jpg");
        }
    });
}

function atualizarImagemDoAnimal(animalId, imageUrl) {
    let animalElement = document.querySelector(`.gallery-item[data-id='${animalId}'] img`);
    if (animalElement) {
        animalElement.src = imageUrl;
    }
}

function exibirDadosNaPagina(data) {
    let nameFarm = document.getElementById("name-farm");
    let descricaoFarm = document.getElementById("descricao-farm");
    let QuantidadeFarm = document.getElementById("quantidade-farm");

    nameFarm.innerText += " " + data.name;
    descricaoFarm.innerText += " " + data.description;
    QuantidadeFarm.innerText += " " + data.animal_quantity;

    const gallery = document.querySelector(".gallery-grid");
    let htmlContent = "";

    data.animals.forEach(animal => {
        htmlContent += `
            <div class="gallery-item" data-id="${animal.id}">
                <img src="caminho/para/imagem_padrao.jpg" alt="${animal.name}">
                <div class="overlay"><span>${animal.name}</span></div>
            </div>
        `;
    });

    gallery.innerHTML = htmlContent;

    document.querySelectorAll(".gallery-item").forEach(item => {
        item.addEventListener("click", () => {
            const animalId = item.getAttribute("data-id"); 
            window.location.href = `animal.html?id=${animalId}`; 
        });
    });
}

document.getElementById("btn-atualizar-fazenda").addEventListener("click", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const farmId = urlParams.get('id'); 

    if (!farmId) {
        console.error("ID da fazenda não encontrado na URL.");
        return; 
    }

    window.location.href = `atualizar-fazenda.html?id=${farmId}`;
});

document.getElementById("btn-cadastrar-animal").addEventListener("click", function() {
    const urlParams = new URLSearchParams(window.location.search);
    const farmId = urlParams.get('id'); 

    if (!farmId) {
        console.error("ID da fazenda não encontrado na URL.");
        return; 
    }

    window.location.href = `cadastro-animal.html?id=${farmId}`;
});



async function deletarFazenda(farmId) {
    // 1. Pede confirmação ao usuário antes de uma ação destrutiva
    const confirmacao = confirm('Tem certeza que deseja excluir esta fazenda? Todos os animais e dados associados serão perdidos permanentemente.');

    if (!confirmacao) {
        console.log("Exclusão cancelada pelo usuário.");
        return; // Para a execução se o usuário clicar em "Cancelar"
    }

    const URL_DELETE = `http://127.0.0.1:8000/farm/${farmId}`;

    try {
        // 2. Faz a requisição para a sua API usando o método DELETE
        const response = await fetch(URL_DELETE, {
            method: 'DELETE',
        });

        // 3. Verifica se a exclusão foi bem-sucedida
        if (response.ok) {
            alert('Fazenda excluída com sucesso!');
            // 4. Redireciona o usuário, pois a página atual não é mais válida
            window.history.back();
        } else {
            // Se o servidor retornou um erro, exibe a mensagem
            const errorData = await response.json();
            alert(`Erro ao excluir a fazenda: ${errorData.detail || 'Ocorreu um erro no servidor.'}`);
        }
    } catch (error) {
        // Captura erros de rede (ex: API offline)
        console.error('Erro na requisição de exclusão:', error);
        alert('Não foi possível conectar ao servidor para excluir a fazenda.');
    }
}

// Como o link de exclusão não tem um ID, precisamos encontrá-lo de outra forma.
// Esta função será executada assim que a página carregar.
document.addEventListener('DOMContentLoaded', () => {
    // Seleciona todos os links com a classe "btn" dentro do container de links
    const todosOsBotoes = document.querySelectorAll('.dashboard-links .btn');
    
    // Procura na lista o link que contém o texto "Deletar Fazenda"
    let btnDeletar = null;
    for (const botao of todosOsBotoes) {
        if (botao.textContent.trim() === 'Deletar Fazenda') {
            btnDeletar = botao;
            break; 
        }
    }

    // Se o botão foi encontrado, adiciona o evento de clique
    if (btnDeletar) {
        btnDeletar.addEventListener('click', function(event) {
            // Impede a ação padrão do link (que seria recarregar a página por causa do href="")
            event.preventDefault(); 
            
            // Reutiliza a mesma lógica que você já usa para pegar o ID da fazenda da URL
            const urlParams = new URLSearchParams(window.location.search);
            const farmId = urlParams.get('id');

            if (farmId) {
                // Chama a função que criamos para fazer a exclusão
                deletarFazenda(farmId);
            } else {
                console.error("ID da fazenda não encontrado na URL para exclusão.");
                alert("Erro: não foi possível identificar a fazenda para exclusão.");
            }
        });
    }
});


window.addEventListener('load', carregarDadosDaFazenda);
