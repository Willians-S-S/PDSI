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

    if (!farmId) {
        alert("O 'farm_id' é obrigatório.");
        return;
    }

    const image = document.getElementById("image").files[0];
    if (!image) {
        alert("A imagem do animal é obrigatória.");
        return;
    }

    const formData = new FormData();
    formData.append("image", image);

    const URL = `http://127.0.0.1:8000/animal/${farmId}/history/inference`;

    console.log([...formData.entries()]);

    fetch(URL, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`
        },
        body: formData
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

