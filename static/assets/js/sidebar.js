document.addEventListener('DOMContentLoaded', function() {
  var toggleButton = document.getElementById('toggleSidebar');
  var sidebar = document.getElementById('sidebar');
  var mainPanel = document.querySelector('.main-panel');

  if (toggleButton && sidebar && mainPanel) {
    toggleButton.addEventListener('click', function() {
      sidebar.classList.toggle('collapsed');
      mainPanel.classList.toggle('sidebar-collapsed');
    });
  }
});