// JavaScript adicional para interatividade

document.addEventListener('DOMContentLoaded', function() {
    // Animações de entrada
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
            }
        });
    }, observerOptions);

    // Observar elementos para animação
    document.querySelectorAll('.card-finance, .chart-container').forEach(el => {
        observer.observe(el);
    });

    // Atualização automática de dados
    function updateLiveData() {
        // Aqui você pode fazer chamadas AJAX para atualizar dados
        console.log('Atualizando dados...');
    }

    // Atualizar a cada 30 segundos
    setInterval(updateLiveData, 30000);
});

// Funções utilitárias
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function showToast(message, type = 'success') {
    // Implementar notificações toast
    console.log(`${type}: ${message}`);
}