document.getElementById("animalForm").addEventListener("submit", function(event) {
    event.preventDefault(); 

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Você precisa estar logado para acessar esta página.');
        window.location.href = 'login.html'; 
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const farmId = urlParams.get('id'); 

    const name = document.getElementById("name").value.trim();
    if (!name) {
        alert("O campo 'Nome do Animal' é obrigatório.");
        return;
    }
    if (!farmId) {
        alert("O 'farm_id' é obrigatório.");
        return;
    }

    const breed = document.getElementById("breed").value.trim();
    let age = document.getElementById("age").value.trim();
    const gender = document.getElementById("gender").value.trim();
    const healthCondition = document.getElementById("health_condition").value.trim();
    const image = document.getElementById("image").files[0];

    if (!image) {
        alert("A imagem do animal é obrigatória.");
        return;
    }

    // Converte age para número (se preenchido)
    age = age ? parseInt(age, 10) : null;

    const formData = new FormData();

    // Adiciona os valores ao FormData (não envia campos vazios)
    formData.append("name", name);
    formData.append("farm_id", farmId);
    formData.append("image", image); // Arquivo obrigatório

    if (breed) formData.append("breed", breed);
    if (age !== null) formData.append("age", age);
    if (gender) formData.append("gender", gender);
    if (healthCondition) formData.append("health_condition", healthCondition);

    const URL = `http://127.0.0.1:8000/animal/`;

    console.log([...formData.entries()]); // Depuração dos dados antes do envio

    fetch(URL, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${token}` // Mantém apenas o cabeçalho Authorization
        },
        body: formData // O próprio FormData define 'Content-Type: multipart/form-data'
    })
    .then(response => {
        return response.json().then(data => {
            if (!response.ok) {
                console.error("Erro da API:", data);
                throw new Error("Erro na requisição: " + response.status);
            }
            return data;
        });
    })
    .then(data => {
        console.log("Sucesso:", data);
        window.location.href = `animal.html?id=${data.id}`;
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro ao cadastrar o animal. Verifique os dados e tente novamente.");
    });
});
