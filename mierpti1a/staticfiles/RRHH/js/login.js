function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

document.getElementById('ingresar-btn').addEventListener('click', function() {
    const folio = document.getElementById('folio').value;
    const password = document.getElementById('password').value;

    fetch('http://127.0.0.1:8000/RRHH/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            folio: folio,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.empleado.puesto === 'Administrador de Recursos Humanos - RRHH' || data.empleado.puesto === 'Gerente de Recursos Humanos - RRHH') {
                window.location.href = '/RRHH/administracion/';
            } else {
                window.location.href = '/RRHH/loginu/';
                alert('No cuentas con un usuario administrador');
            }
        } else {
            alert(data.error);
        }
    })
    .catch(error => console.error('Error:', error));
});