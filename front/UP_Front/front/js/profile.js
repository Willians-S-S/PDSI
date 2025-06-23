function carregarDadosDaAPI() {
    const token = localStorage.getItem('token');
    
    const email = getEmailFromJWT(token);
    
    const URL = `http://localhost:8000/user/email/${email}`;
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
            return response.json();
        })
        .then(data => {
            const defaultImageUrl = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"; 
            const URL_IMAGE = `http://127.0.0.1:8000/images/${data.profile_picture}` 

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

                    if (imageBlob.size === 0) {
                        console.warn("A imagem está vazia. Usando imagem padrão.");
                        throw new Error("Imagem vazia ou inválida");
                    }

                    console.log(data)

                    let image = window.URL.createObjectURL(imageBlob);
                    exibirDadosNaPagina(data, image);
                })
                .catch(error => {
                    console.error("Erro ao carregar a imagem:", error);
                    exibirDadosNaPagina(data, defaultImageUrl);
                });
        })
        .catch(error => {
            alert('Você precisa estar logado para acessar esta página.');
            window.location.href = 'login.html';
        });
}

function getEmailFromJWT(token) {
  try {
    const payloadBase64 = token.split('.')[1]; // segunda parte do JWT
    const decodedPayload = JSON.parse(atob(payloadBase64));
    console.log("Payload decodificado:", decodedPayload.sub);
    return decodedPayload.sub; // ou o nome da chave correta
  } catch (error) {
    console.error("Erro ao decodificar JWT:", error);
    return null;
  }
}

function exibirDadosNaPagina(data, image) {

    let login = document.getElementById("login-link");
    let signup = document.getElementById("signup-link");

    adicionarBotaoSair()
    
    login.parentElement.remove();
    signup.parentElement.remove();

    const nameUser = document.getElementById('name-user');
    nameUser.innerText += " " + data.name;

    
    const profileImage = document.getElementById("profile-image");
    profileImage.src = image;

    const gallery = document.querySelector(".gallery-grid");

    let htmlContent = "";
    data.farms.forEach(fazenda => {
        htmlContent += `
            <div class="gallery-item" data-id="${fazenda.id}">
            
                // <img src="https://get.pxhere.com/photo/landscape-tree-nature-grass-fence-field-farm-meadow-countryside-air-morning-summer-pasture-ranch-agriculture-waterway-clouds-dutch-landscape-rural-area-outdoor-structure-home-fencing-685532.jpg" alt="${fazenda.name}">
                <div class="overlay"><span>${fazenda.name}</span></div>
            </div>
        `;
    });

    gallery.innerHTML = htmlContent;

    const galleryItems = document.querySelectorAll(".gallery-item");

    galleryItems.forEach(item => {
        item.addEventListener("click", () => {
            const farmId = item.getAttribute("data-id"); 
            window.location.href = `farm.html?id=${farmId}`; 
        })
    });
}

function adicionarBotaoSair(){
    let navLinks = document.getElementById("nav-links");
    let logoutItem = document.createElement("li");
  
    let logoutLink = document.createElement("a");
    logoutLink.href = "#"; 
    logoutLink.id = "logout-link";
    logoutLink.textContent = "Sair";
  
    logoutLink.addEventListener("click", function (event) {
        event.preventDefault(); 
        localStorage.removeItem("token"); 
        window.location.href = "index.html"; 
  
    });
  
    logoutItem.appendChild(logoutLink);
    navLinks.appendChild(logoutItem);
  }

document.getElementById("excluir-user").addEventListener("click", () => {
    let deletar = confirm("Tem certeza que deseja excluir sua conta?");
    
    if (!deletar){
        return;
    }
    
    const URL = 'http://localhost:8000/user/';
    const token = localStorage.getItem('token');

    if (!token) {
        console.error("Token não encontrado no localStorage.");
        return;
    }

    fetch(URL, {
        method: 'DELETE',
        headers: {  
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.status == 401) {
            throw new Error("Não autorizado. Verifique seu token de autenticação.");
        }
        if (response.status != 204) {
            throw new Error(`Erro na requisição: ${response.statusText}`);
        }
        localStorage.removeItem('token');
        alert("Conta excluída com sucesso!");
        window.location.href = 'index.html';  
    })
    .catch(error => {
        console.error("Erro:", error);
    });
});



window.addEventListener('load', carregarDadosDaAPI);