function addItem() {
    const itemContainer = document.getElementById('item_container');
    const newItem = document.createElement('div');
    newItem.className = 'item';
    newItem.innerHTML = `
        <input type="text" name="item_name" placeholder="Nama Barang">
        <input type="text" name="item_price" placeholder="Harga Barang">
    `;
    itemContainer.appendChild(newItem);
}

function calculateTotal() {
    const items = [];
    document.querySelectorAll('.item').forEach(item => {
        const itemName = item.querySelector('input[name="item_name"]').value;
        const itemPrice = parseFloat(item.querySelector('input[name="item_price"]').value);
        items.push({ name: itemName, price: itemPrice });
    });

    fetch('/transaksi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('total_belanja').innerText = `Total Harga yang harus dibayar adalah: Rp. ${data.total_belanja.toLocaleString('id-ID')}`;
        if (data.voucher_code) {
            document.getElementById('voucher_form').style.display = 'block';
        }
        document.getElementById('reset_button').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
}

function applyVoucher() {
    const voucherCode = document.getElementById('voucher_code').value;
    const totalBelanjaText = document.getElementById('total_belanja').innerText;
    const totalBelanja = parseFloat(totalBelanjaText.replace(/[^\d]/g, ''));

    fetch('/apply_voucher', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voucher_code: voucherCode, total_belanja: totalBelanja })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Voucher berhasil digunakan! Nominal: Rp. ${data.nominal.toLocaleString('id-ID')}`);
            document.getElementById('total_belanja').innerText = `Total Harga yang harus dibayar setelah voucher: Rp. ${data.new_total.toLocaleString('id-ID')}`;
        } else {
            alert('Voucher tidak valid atau sudah digunakan.');
        }
    })
    .catch(error => console.error('Error:', error));
}

function resetForm() {
    document.getElementById('item_form').reset();
    document.getElementById('voucher_form').style.display = 'none';
    document.getElementById('reset_button').style.display = 'none';
    document.getElementById('total_belanja').innerText = '';
    const itemContainer = document.getElementById('item_container');
    while (itemContainer.children.length > 1) {
        itemContainer.removeChild(itemContainer.lastChild);
    }
}
