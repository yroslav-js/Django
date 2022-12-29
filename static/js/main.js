const menuButton = document.getElementById('menu__toggle');
const overlay = document.querySelector('.overlay');
const sidebarMenu = document.querySelector('.sidebar-menu');

if (menuButton != null) {
        menuButton.addEventListener('click', () => {
        overlay.classList.toggle('overlay_active');
        sidebarMenu.classList.toggle('sidebar-menu_active');
    });
}

if (overlay != null) {
    overlay.addEventListener('click', () => {
        overlay.classList.remove('overlay_active');
        sidebarMenu.classList.remove('sidebar-menu_active');
        menuButton.checked = false;
    });
}