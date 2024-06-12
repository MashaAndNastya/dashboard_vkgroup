document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('#copy_link_button').addEventListener('click', function () {
        var copyText = document.querySelector('#hidden_clipboard');
        copyText.style.display = 'block';  // make input visible
        copyText.select();
        document.execCommand("copy");
        copyText.style.display = 'none';  // hide input again
        alert('Ссылка скопирована в буфер обмена: ' + copyText.value);
    });
});
