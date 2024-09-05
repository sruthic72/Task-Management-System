document.getElementById('registrationForm').addEventListener('submit', function(event) {
    const name = document.getElementById('name').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!name || !username || !email || !password) {
        alert('Please fill in all fields.');
        event.preventDefault(); // Prevent form from submitting
    }
});
