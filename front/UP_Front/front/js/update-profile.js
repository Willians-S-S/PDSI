let currentUserId = null;

/**
 * Decodifica o payload de um token JWT para extrair o subject (email).
 */
function getEmailFromJWT(token) {
    try {
        const payloadBase64 = token.split('.')[1];
        const decodedPayload = JSON.parse(atob(payloadBase64));
        return decodedPayload.sub;
    } catch (error) {
        console.error("Erro ao decodificar JWT:", error);
        return null;
    }
}

/**
 * Adiciona um botão "Sair" dinamicamente à barra de navegação.
 */
function adicionarBotaoSair() {
    if (document.getElementById("logout-link")) return;

    let navLinks = document.querySelector(".nav-links");
    if (!navLinks) {
        console.error("Elemento '.nav-links' não encontrado no HTML.");
        return;
    }

    const loginLink = document.querySelector('a[href="login.html"]');
    const signupLink = document.querySelector('a[href="signup.html"]');
    if (loginLink) loginLink.parentElement.remove();
    if (signupLink) signupLink.parentElement.remove();

    let logoutItem = document.createElement("li");
    let logoutLink = document.createElement("a");
    logoutLink.href = "#";
    logoutLink.id = "logout-link";
    logoutLink.textContent = "Sair";

    logoutLink.addEventListener("click", (event) => {
        event.preventDefault();
        localStorage.removeItem("token");
        window.location.href = "index.html";
    });

    logoutItem.appendChild(logoutLink);
    navLinks.appendChild(logoutItem);
}

/**
 * Preenche os campos do formulário com os dados do usuário.
 */
function preencherFormulario(data) {
    const defaultImageUrl = "https://via.placeholder.com/150";
    document.getElementById("profile-pic").src = data.image_url || defaultImageUrl;
    document.getElementById("nome").value = data.name || '';
    document.getElementById("email").value = data.email || '';
    document.getElementById("username").value = data.username || '';
    document.getElementById("cpf").value = data.cpf || '';
    document.getElementById("tipo_usuario").value = data.role || 'cuidador';
}

/**
 * Busca os dados do usuário na API e inicia o preenchimento da página.
 */
async function carregarDadosPerfil() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Você precisa estar logado para acessar esta página.');
        window.location.href = 'login.html';
        return;
    }

    const email = getEmailFromJWT(token);
    if (!email) {
        alert('Token inválido. Faça o login novamente.');
        localStorage.removeItem('token');
        window.location.href = 'login.html';
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/user/email/${email}`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 401 || response.status === 403) {
            throw new Error('Sessão expirada ou não autorizada.');
        }
        if (!response.ok) {
            throw new Error('Falha ao buscar dados do usuário.');
        }

        const userData = await response.json();
        currentUserId = userData.id;

        preencherFormulario(userData);
        adicionarBotaoSair();

    } catch (error) {
        console.error("Erro no processo de carregamento do perfil:", error);
        alert(error.message + ' Redirecionando para o login.');
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    }
}

// --- Event Listeners ---

document.addEventListener('DOMContentLoaded', carregarDadosPerfil);

// 2. ATUALIZAR DADOS (SUBMIT DO FORMULÁRIO)
document.getElementById("update-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!currentUserId) {
        alert("Erro: ID do usuário não encontrado. Recarregue a página.");
        return;
    }

    const token = localStorage.getItem('token');
    const formData = new FormData();

    formData.append("name", document.getElementById("nome").value);
    formData.append("username", document.getElementById("username").value);
    formData.append("email", document.getElementById("email").value);
    formData.append("cpf", document.getElementById("cpf").value);
    formData.append("role", document.getElementById("tipo_usuario").value);

    const password = document.getElementById("password").value;
    if (password) {
        formData.append("password", password);
    }

    const fileInput = document.getElementById("fotoperfil");
    if (fileInput && fileInput.files.length > 0) {
        formData.append("image", fileInput.files[0]);
    }

    try {
        const response = await fetch(`http://localhost:8000/user/${currentUserId}`, {
            method: "PUT",
            headers: {
                'Authorization': `Bearer ${token}`
                // Importante: **NÃO** defina manualmente o `Content-Type` com multipart, o browser faz isso.
            },
            body: formData
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Ocorreu um erro ao atualizar os dados.");
        }

        await response.json();
        alert("Dados atualizados com sucesso!");
        window.location.href = "profile.html";

    } catch (error) {
        console.error("Erro na atualização:", error);
        alert(`Erro: ${error.message}`);
    }
});

// 3. EXCLUIR CONTA
document.getElementById("excluir-user-btn").addEventListener("click", async () => {
    if (!confirm("Tem certeza que deseja EXCLUIR sua conta? Esta ação é PERMANENTE.")) {
        return;
    }

    if (!currentUserId) {
        alert("Erro: ID do usuário não encontrado. Recarregue a página.");
        return;
    }

    const token = localStorage.getItem('token');

    try {
        const response = await fetch(`http://localhost:8000/user/${currentUserId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.status === 204) {
            localStorage.removeItem('token');
            alert("Conta excluída com sucesso!");
            window.location.href = 'index.html';
        } else {
            const err = await response.json();
            throw new Error(err.detail || 'Não foi possível excluir a conta.');
        }
    } catch (error) {
        console.error("Erro ao excluir conta:", error);
        alert(`Erro: ${error.message}`);
    }
});

