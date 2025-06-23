document.getElementById("animalForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const token = localStorage.getItem('token');
    if (!token) {
        alert('Você precisa estar logado para acessar esta página.');
        window.location.href = 'login.html';
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const animalID = urlParams.get('id');

    const name = document.getElementById("name").value.trim();
    const breed = document.getElementById("breed").value.trim();
    let age = document.getElementById("age").value.trim();
    const gender = document.getElementById("gender").value.trim();
    const healthCondition = document.getElementById("health_condition").value.trim();

    age = age ? parseInt(age, 10) : null;

    const animalData = {
        name: name || null,
        breed: breed || null,
        age: age,
        gender: gender || null,
        health_condition: healthCondition || null
    };

    const URL = `http://127.0.0.1:8000/animal/${animalID}`;
    console.log(animalData);

    fetch(URL, {
        method: "PUT",
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(animalData)
    })
    .then(response => response.json().then(data => {
        if (!response.ok) {
            console.error("Erro da API:", data);
            throw new Error("Erro na requisição: " + response.status);
        }
        return data;
    }))
    .then(data => {
        console.log("Sucesso:", data);
        window.location.href = `animal.html?id=${data.id}`;
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro ao cadastrar o animal. Verifique os dados e tente novamente.");
    });
});

