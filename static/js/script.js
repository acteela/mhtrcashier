document.getElementById('add_item_button').addEventListener('click', function() {
    let itemsDiv = document.getElementById('items');
    let newItemDiv = document.createElement('div');
    newItemDiv.classList.add('item');
    newItemDiv.innerHTML = `
        <input type="text" placeholder="Nama Barang" class="item-name">
        <input type="text" placeholder="Harga Barang" class="item-price">
    `;
    itemsDiv.appendChild(newItemDiv);
});

document.getElementById('calculate_button').addEventListener('click', function() {
    let items = [];
    let itemElements = document.querySelectorAll('.item');
    itemElements.forEach(function(item) {
        let name = item.querySelector('.item-name').value;
        let price = item.querySelector('.item-price').value;
        items.push({name: name, price: price});
    });

    fetch('/transaksi', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({items: items})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('total_label').innerText = `Total Harga yang harus dibayar adalah: Rp. ${data.total_belanja}`;
        if (data.voucher_code) {
            alert(`Selamat! Anda mendapatkan voucher belanja Rp.${data.voucher_nominal}\nKode Voucher: ${data.voucher_code}`);
        }
        document.getElementById('reset_button').style.display = 'inline-block';
    });
});

document.getElementById('reset_button').addEventListener('click', function() {
    document.getElementById('items').innerHTML = `
        <div class="item">
            <input type="text" placeholder="Nama Barang" class="item-name">
            <input type="text" placeholder="Harga Barang" class="item-price">
        </div>
    `;
    document.getElementById('total_label').innerText = '';
    document.getElementById('reset_button').style.display = 'none';
});
