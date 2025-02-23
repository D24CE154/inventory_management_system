const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');
const signInBtn = document.querySelector('.sign-in button');

registerBtn.addEventListener('click', () => {
    container.classList.add("active");
});

loginBtn.addEventListener('click', () => {
    container.classList.remove("active");
});

signInBtn.addEventListener('click', (event) => {
    event.preventDefault(); 
    window.location.href = "../Dashboard/Dashboard.html"; 
});
