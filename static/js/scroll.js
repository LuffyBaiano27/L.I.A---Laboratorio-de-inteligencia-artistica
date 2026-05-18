document.addEventListener("DOMContentLoaded", function() {
    const vid1 = document.getElementById('vid1');
    const vid2 = document.getElementById('vid2');
    const vid3 = document.getElementById('vid3');

    // LÓGICA DE TRANSIÇÃO DOS VÍDEOS DE FUNDO
    window.addEventListener('scroll', () => {
        let scrollY = window.scrollY;
        let vh = window.innerHeight;

        if (scrollY < vh) {
            let progress = scrollY / vh;
            vid1.style.opacity = 1 - progress;
            vid2.style.opacity = progress;
            vid3.style.opacity = 0;
        } else if (scrollY >= vh && scrollY < 2 * vh) {
            let progress = (scrollY - vh) / vh;
            vid1.style.opacity = 0;
            vid2.style.opacity = 1 - progress;
            vid3.style.opacity = progress;
        } else {
            vid1.style.opacity = 0;
            vid2.style.opacity = 0;
            vid3.style.opacity = 1;
        }
    });

    // LÓGICA DE REVEAL DOS CARDS (AQUI ESTÁ A CORREÇÃO!)
    // Agora o JS procura por todos os elementos que tenham reveal-left ou reveal-right
    const reveals = document.querySelectorAll('.reveal-left, .reveal-right');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, {
        // Reduzi um pouco para 0.2 para o card aparecer um pouquinho mais cedo na tela
        threshold: 0.2 
    });

    reveals.forEach(reveal => {
        revealObserver.observe(reveal);
    });
});