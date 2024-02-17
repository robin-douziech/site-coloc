function showHamburgerDropDownMenu() {
	document.querySelector(".hamburger-dropdown-menu").style.display = "flex";
	document.querySelector(".hamburger-menu > a").removeEventListener("click", showHamburgerDropDownMenu);
	document.querySelector(".hamburger-menu > a").addEventListener("click", hideHamburgerDropDownMenu);
}

function hideHamburgerDropDownMenu() {
	document.querySelector(".hamburger-dropdown-menu").style.display = "none";
	document.querySelector(".hamburger-menu > a").removeEventListener("click", hideHamburgerDropDownMenu);
	document.querySelector(".hamburger-menu > a").addEventListener("click", showHamburgerDropDownMenu);
}

document.addEventListener("DOMContentLoaded", function() {
	document.querySelector(".hamburger-menu > a").addEventListener("click", showHamburgerDropDownMenu);
});