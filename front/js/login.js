document.getElementById('login-btn').addEventListener('click', function (event) {
    event.preventDefault(); // Evita o comportamento padrão do formulário

    const URL = 'http://127.0.0.1:8000/user/token'; 

    // Obter os valores dos campos de entrada
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Criar os dados para enviar
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    // Enviar a requisição POST ao backend
    fetch(URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro na requisição: ${response.status}`);
        }
        return response.json(); // Converter a resposta para JSON
    })
    .then(data => {
        console.log('Resposta da API:', data);
        // window.alert('Login bem-sucedido!');

        // Verificar se o token foi retornado
        if (data.access_token) {
            // Armazenar o token no localStorage
            localStorage.setItem('token', data.access_token);
            console.log('Token armazenado:', data.access_token);

            // Redirecionar para a página de perfil
            window.location.href = 'profile.html';
        } else {
            throw new Error('Token não encontrado na resposta.');
        }
    })
    .catch(error => {
        console.error('Erro ao fazer login:', error);
        alert('Erro ao fazer login. Verifique suas credenciais.');
    });
});
