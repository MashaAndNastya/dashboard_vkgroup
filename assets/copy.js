// assets/copy.js
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('copy_token_button').addEventListener('click', function () {
        var tokenDisplay = document.getElementById('token_display');
        var range = document.createRange();
        range.selectNode(tokenDisplay);
        window.getSelection().removeAllRanges();  // Clear current selection
        window.getSelection().addRange(range);  // To select the element's text content
        document.execCommand('copy');
        window.getSelection().removeAllRanges();  // Deselect after copy
        alert('Токен скопирован в буфер обмена');
    });
});
