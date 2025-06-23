document.getElementById("cadastrar-btn").addEventListener("click", function (event) {
    event.preventDefault(); 

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Você precisa estar logado para acessar esta página.');
        window.location.href = 'login.html'; 
    }
    
    let formData = {
        name: document.getElementById("nomeFazenda").value,
        description: document.getElementById("descricao").value,
        animal_quantity: document.getElementById("quantidadeAnimal").value
    }

    const URL = "http://127.0.0.1:8000/farm/";

    fetch(URL, {
        method: "POST",
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData) 
    })
    .then(response => {
        if (response.status == 401){
            alert('Você precisa estar logado para acessar esta página.');
            window.location.href = 'login.html'; 
        }
        if (!response.ok) {
            throw new Error("Erro na requisição: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        window.location.href = `farm.html?id=${data.id}`
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro ao criar conta. Verifique os dados e tente novamente.");
    });
});
