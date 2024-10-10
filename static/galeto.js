document.addEventListener('DOMContentLoaded', function () {
    const tipoGaleto = document.getElementById('tipo_galeto');
    const feijaoDivGaleto = document.getElementById('feijao_div_galeto');
    const acompanhamentosGaleto = document.getElementById('acompanhamentos_galeto');

    tipoGaleto.addEventListener('change', function () {
        const selectedValue = tipoGaleto.value;

        // Verifica se o galeto selecionado permite feijão
        if (selectedValue === 'completo' || selectedValue === 'meio') {
            feijaoDivGaleto.style.display = 'block';
            acompanhamentosGaleto.textContent = 'Acompanhamentos: arroz, feijão, farofa,  vinagrete e batata frita';
        } else {
            feijaoDivGaleto.style.display = 'none';
            acompanhamentosGaleto.textContent = 'Acompanhamentos: farofa, vinagrete e batata frita.';
        }
    });
});document.addEventListener('DOMContentLoaded', function () {
    const tipoGaleto = document.getElementById('tipo_galeto');
    const feijaoDivGaleto = document.getElementById('feijao_div_galeto');
    const feijaoGaleto = document.getElementById('feijao_galeto'); // Certifique-se que este elemento existe
    const acompanhamentosGaleto = document.getElementById('acompanhamentos_galeto');

    tipoGaleto.addEventListener('change', function () {
        const selectedValue = tipoGaleto.value;

        // Verifica se o galeto selecionado permite feijão
        if (selectedValue === 'completo' || selectedValue === 'meio') {
            feijaoDivGaleto.style.display = 'block'; // Exibe o campo de feijão
            feijaoGaleto.setAttribute('required', true); // Torna o feijão obrigatório
            acompanhamentosGaleto.textContent = 'Acompanhamentos: arroz, feijão, farofa,  vinagrete e batata frita.';
        } else {
            feijaoDivGaleto.style.display = 'none'; // Esconde o campo de feijão
            feijaoGaleto.removeAttribute('required'); // Remove a obrigatoriedade do feijão
            acompanhamentosGaleto.textContent = 'Acompanhamentos: farofa, vinagrete e batata frita.';
        }
    });

    // Verificação inicial ao carregar a página, caso já tenha algum valor selecionado
    if (tipoGaleto.value === 'completo' || tipoGaleto.value === 'meio') {
        feijaoDivGaleto.style.display = 'block'; // Exibe o campo de feijão
        feijaoGaleto.setAttribute('required', true); // Torna o feijão obrigatório
        acompanhamentosGaleto.textContent = 'Acompanhamentos: arroz, feijão, farofa,  vinagrete e batata frita.';
    } else if (tipoGaleto.value === 'simples') {
        feijaoDivGaleto.style.display = 'none'; // Esconde o campo de feijão
        feijaoGaleto.removeAttribute('required'); // Remove a obrigatoriedade
        acompanhamentosGaleto.textContent = 'Acompanhamentos: farofa, vinagrete e batata frita.';
    }
});

