document.getElementById("signup-btn").addEventListener("click", function (event) {
    event.preventDefault(); 

    console.log("Iniciando requisição...");

    const URL = "http://localhost:8000/user/";

    const formData = new FormData();        

    formData.append("name", document.getElementById("nome").value);
    formData.append("username", document.getElementById("username").value);
    formData.append("email", document.getElementById("email").value);
    formData.append("password", document.getElementById("password").value);
    formData.append("cpf", document.getElementById("cpf").value);

    // Novo campo adicionado: tipo de usuário
    const tipoUsuario = document.getElementById("tipo_usuario").value;
    formData.append("role", tipoUsuario);

    const fileInput = document.getElementById("fotoperfil");
    const file = fileInput.files[0];

    if (!file) {
        console.error("Nenhum arquivo selecionado.");
        alert("Por favor, selecione uma foto de perfil.");
        return;
    }

    formData.append("image", file); 

    console.log("Enviando dados para API...");

    fetch(URL, {
        method: "POST",
        body: formData 
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Erro na requisição: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log("Sucesso:", data);
        alert("Conta criada com sucesso!");
        window.location.href = "login.html";
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro ao criar conta. Verifique os dados e tente novamente.");
    });
});
