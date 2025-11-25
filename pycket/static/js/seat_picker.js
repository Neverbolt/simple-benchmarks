document.querySelectorAll('.s label').forEach(label => {
    label.addEventListener('click', () => {
        const input = label.previousElementSibling;
        if (input.hasAttribute('disabled')) {
            return false;
        }

        const seats = document.getElementById('num_seats');
        const count = parseInt(seats.value) + (input.checked ? -1 : 1);
        seats.value = count;

        const form = document.querySelector('form');
        const submitButton = form.querySelector('button[type="submit"]');
        const funds = parseFloat(document.getElementById('customer-balance').innerText);
        const price = parseFloat(document.getElementById('event-price').innerText);
        console.log("funds: " + funds + ", price: " + price + ", count: " + count + ", total: " + count * price);
        if (count * price > funds) {
            document.getElementById('error').innerText = 'Insufficient funds.';
            submitButton.setAttribute("disabled", "true");
            form.setAttribute("disabled", "true");
        } else {
            document.getElementById('error').innerText = '';
            submitButton.removeAttribute("disabled");
            form.removeAttribute("disabled");
        }
    });
});
