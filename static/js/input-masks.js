
document.addEventListener('DOMContentLoaded', function () {

    function applyPhoneMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 11) value = value.slice(0, 11);

        if (value.length > 10) {
            // (XX) XXXXX-XXXX
            value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
        } else if (value.length > 5) {
            // (XX) XXXX-XXXX
            value = value.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
        } else if (value.length > 2) {
            // (XX) ...
            value = value.replace(/^(\d{2})(\d{0,5}).*/, '($1) $2');
        } else {
            // (XX...
            if (value.length > 0) {
                value = value.replace(/^(\d*)/, '($1');
            }
        }
        input.value = value;
    }

    function applyCepMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 8) value = value.slice(0, 8);

        if (value.length > 5) {
            value = value.replace(/^(\d{5})(\d{0,3}).*/, '$1-$2');
        }
        input.value = value;
    }

    function applyDocumentMask(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length > 14) value = value.slice(0, 14);

        if (value.length <= 11) {
            // CPF Mask Logic
            // 000.000.000-00
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        } else {
            // CNPJ Mask Logic
            // 00.000.000/0000-00
            value = value.replace(/^(\d{2})(\d)/, '$1.$2');
            value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
            value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
            value = value.replace(/(\d{4})(\d)/, '$1-$2');
        }
        input.value = value;
    }

    // Attach listeners
    const phoneInputs = document.querySelectorAll('.mask-phone');
    phoneInputs.forEach(input => {
        input.addEventListener('input', (e) => applyPhoneMask(e.target));
        // Apply on load if value exists
        if (input.value) applyPhoneMask(input);
    });

    const cepInputs = document.querySelectorAll('.mask-cep');
    cepInputs.forEach(input => {
        input.addEventListener('input', (e) => applyCepMask(e.target));
        if (input.value) applyCepMask(input);
    });

    const docInputs = document.querySelectorAll('.mask-document');
    docInputs.forEach(input => {
        input.addEventListener('input', (e) => applyDocumentMask(e.target));
        if (input.value) applyDocumentMask(input);
    });
});
