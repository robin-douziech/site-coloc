function showCreateDropDownMenu() {
	document.querySelector(".create-dropdown-menu").style.display = "flex";
	document.querySelector(".create-btn > a").removeEventListener("click", showCreateDropDownMenu);
	document.querySelector(".create-btn > a").addEventListener("click", hideCreateDropDownMenu);
}

function hideCreateDropDownMenu() {
	document.querySelector(".create-dropdown-menu").style.display = "none";
	document.querySelector(".create-btn > a").removeEventListener("click", hideCreateDropDownMenu);
	document.querySelector(".create-btn > a").addEventListener("click", showCreateDropDownMenu);
}

document.addEventListener("DOMContentLoaded", function() {
	document.querySelector(".create-btn > a").addEventListener("click", showCreateDropDownMenu);
});