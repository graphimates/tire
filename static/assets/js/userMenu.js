document.addEventListener("DOMContentLoaded", function() {
  const userImage = document.getElementById('userImage');
  const dropdownMenu = document.getElementById('dropdownMenu');

  userImage.addEventListener('click', function() {
    dropdownMenu.style.display = dropdownMenu.style.display === 'none' ? 'block' : 'none';
  });

  window.addEventListener('click', function(e) {
    if (!userImage.contains(e.target) && !dropdownMenu.contains(e.target)) {
      dropdownMenu.style.display = 'none';
    }
  });
});
