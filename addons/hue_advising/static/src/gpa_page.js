/** @odoo-module **/

document.addEventListener('DOMContentLoaded', () => {
    const menuLinks = document.querySelectorAll("div.bhoechie-tab-menu>div.list-group>a");
    const tabContents = document.querySelectorAll("div.bhoechie-tab>div.bhoechie-tab-content");

    menuLinks.forEach((link, index) => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelector("div.bhoechie-tab-menu>div.list-group>a.active")?.classList.remove("active");
            link.classList.add("active");

            tabContents.forEach(content => content.classList.remove("active"));
            tabContents[index].classList.add("active");
        });
    });
});
