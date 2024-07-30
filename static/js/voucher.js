document.getElementById('voucher_form').addEventListener('submit', function(event) {
    event.preventDefault();
    let voucherCode = document.getElementById('voucher_code').value;

    fetch('/apply_voucher', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({voucher_code: voucherCode})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Voucher berhasil digunakan! Diskon: Rp. ${data.nominal}`);
            window.location.href = '/transaksi';
        } else {
            alert('Kode voucher tidak valid atau sudah digunakan!');
        }
    });
});
