/*************************************************
 * 🔊 MOTOR DE SONIDOS
 *************************************************/
const AudioEngine = (() => {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();

    function beep({ frequency = 440, duration = 0.15, volume = 0.25, type = 'sine' }) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = type;
        osc.frequency.value = frequency;
        gain.gain.value = volume;

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + duration);
    }

    return {
        newOrder() {
            beep({ frequency: 900, duration: 0.2 });
        },
        updateOrder() {
            beep({ frequency: 650, duration: 0.12 });
            setTimeout(() => beep({ frequency: 650, duration: 0.12 }), 150);
        },
        warning() {
            beep({ frequency: 420, duration: 0.35, type: 'triangle' });
        },
        danger() {
            beep({ frequency: 220, duration: 0.5, type: 'sawtooth' });
            setTimeout(() => beep({ frequency: 180, duration: 0.5, type: 'sawtooth' }), 600);
        }
    };
})();

/*************************************************
 * 🍳 MÓDULO COCINA
 *************************************************/
document.addEventListener('DOMContentLoaded', function () {

    const board = document.getElementById('kitchen-board');
    let previousOrders = {};

    // 🔓 desbloquear audio
    document.addEventListener('click', () => {
        AudioEngine.newOrder();
    }, { once: true });

    function loadKitchen() {
        fetch('/pos/kitchen/orders/')
            .then(res => res.json())
            .then(data => {

                board.innerHTML = '';

                if (!data.length) {
                    board.innerHTML = `
                        <div class="col-12 text-center text-muted">
                            No hay pedidos en cocina 🍳
                        </div>`;
                    previousOrders = {};
                    return;
                }

                data.forEach(order => {

                    const now = Date.now();
                    const createdAt = new Date(order.created_at).getTime();
                    const minutes = Math.floor((now - createdAt) / 60000);

                    let cardState = '';
                    let badgeClass = 'time-ok';
                    let sound = null;

                    if (minutes >= 15) {
                        cardState = 'danger';
                        badgeClass = 'time-danger';
                        sound = 'danger';
                    } else if (minutes >= 7) {
                        cardState = 'warning';
                        badgeClass = 'time-warning';
                        sound = 'warning';
                    }

                    // 🆕 nuevo pedido
                    if (!previousOrders[order.order_id]) {
                        AudioEngine.newOrder();
                    }

                    // 🔄 pedido actualizado
                    if (
                        previousOrders[order.order_id] &&
                        previousOrders[order.order_id] !== order.items.length
                    ) {
                        AudioEngine.updateOrder();
                    }

                    // 🔔 cambio de estado por tiempo
                    if (
                        previousOrders[order.order_id + '_state'] !== cardState &&
                        sound
                    ) {
                        AudioEngine[sound]();
                    }

                    previousOrders[order.order_id] = order.items.length;
                    previousOrders[order.order_id + '_state'] = cardState;

                    let itemsHTML = '';
                    order.items.forEach(i => {
                        itemsHTML += `
                            <div class="kitchen-item">
                                <span class="product">${i.product}</span>
                                <span class="qty">${i.qty}</span>
                            </div>
                        `;
                    });

                    board.innerHTML += `
                        <div class="col-12 col-md-6 col-lg-3 d-flex">
                            <div class="kitchen-card w-100 d-flex flex-column ${cardState}">

                                <div class="kitchen-header">
                                    <span class="table-name">${order.table}</span>
                                    <span class="time-badge ${badgeClass}">
                                        ${minutes} min
                                    </span>
                                </div>

                                <div class="kitchen-items">
                                    ${itemsHTML}
                                </div>

                                <!-- 👇 SIEMPRE ABAJO -->
                                <div class="kitchen-actions mt-auto pt-3">
                                    <button 
                                        type="button",
                                        class=" btn-ready"
                                        data-id="${order.order_id}">
                                        ✔ listo
                                    </button>
                                </div>

                            </div>
                        </div>
                    `;
                });
            });
    }

    loadKitchen();
    setInterval(loadKitchen, 5000);
});

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('btn-ready')) {

        e.preventDefault();
        e.stopPropagation();

        const btn = e.target;
        const orderId = btn.dataset.id;

        btn.disabled = true;
        btn.innerHTML = '⏳';

        fetch(`/pos/kitchen/order/${orderId}/ready/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            }
        })
        .then(res => {
            if (!res.ok) {
                throw new Error('Respuesta no válida');
            }
            return res.json(); // 👈 solo si es OK
        })
        .then(data => {
            if (data.success) {
                toastr.success('Pedido listo 🍽️');
                loadKitchen();
            } else {
                toastr.error(data.message || 'No se pudo marcar el pedido');
                btn.disabled = false;
                btn.innerHTML = '✔ listo';
            }
        })
        .catch(() => {
            toastr.error('Error al marcar pedido');
            btn.disabled = false;
            btn.innerHTML = '✔ listo';
        });
    }
});

function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
}

function equalizeKitchenCards() {
    const cards = document.querySelectorAll('.kitchen-card');
    let maxHeight = 0;

    // Resetear alturas
    cards.forEach(card => {
        card.style.height = 'auto';
    });

    // Calcular la mayor
    cards.forEach(card => {
        maxHeight = Math.max(maxHeight, card.offsetHeight);
    });

    // Aplicar la mayor a todos
    cards.forEach(card => {
        card.style.height = maxHeight + 'px';
    });
}
