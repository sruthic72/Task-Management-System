document.getElementById('registrationForm').addEventListener('submit', function(event) {
    const fname = document.getElementById('first_name').value;
    const lname = document.getElementById('last_name').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    // const password = document.getElementById('password').value;

    if (!fname || !lname || !username || !email || !password) {
        alert('Please fill in all fields.');
        event.preventDefault(); // Prevent form from submitting
    }

    const password = document.getElementById('password').value;
    const password2 = document.getElementById('password2').value;

    if (password !== password2) {
        alert('Passwords do not match.');
        event.preventDefault();  // Prevent the form from submitting
    }
});
