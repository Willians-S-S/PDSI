document.getElementById("cadastrar-btn").addEventListener("click", function (event) {
    event.preventDefault(); 

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Você precisa estar logado para acessar esta página.');
        window.location.href = 'login.html'; 
    }
    
    let formData = {
        name: document.getElementById("nomeFazenda").value.trim() || null,
        description: document.getElementById("descricao").value.trim() || null,
        animal_quantity: document.getElementById("quantidadeAnimal").value.trim() || null
    };
    

    console.log(formData);


    const urlParams = new URLSearchParams(window.location.search);
    const farmId = urlParams.get('id'); 

    const URL = `http://127.0.0.1:8000/farm/${farmId}`;


    fetch(URL, {
        method: "PUT",
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
