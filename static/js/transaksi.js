fetch('/get_transaction_detail')
    .then(response => response.json())
    .then(data => {
        document.getElementById('transaction_detail').innerText = `Total: Rp. ${data.total}, Voucher: ${data.voucher_code ? data.voucher_code : 'Tidak ada'}`;
    });
