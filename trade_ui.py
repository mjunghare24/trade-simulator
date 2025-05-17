from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QLineEdit, QPushButton
import threading
import sys
from ui_logic import start_websocket  # Make sure ui_logic.py is in the same folder

class TradeSimulatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Trade Simulator')
        main_layout = QHBoxLayout()

        # Left Panel - Input parameters
        left_layout = QVBoxLayout()
        self.asset_selector = QComboBox()
        self.asset_selector.addItems(['BTC-USDT', 'ETH-USDT', 'SOL-USDT'])
        self.quantity_input = QLineEdit('100')
        self.fee_tier_input = QLineEdit('tier1')
        self.start_button = QPushButton('Start Simulation')

        left_layout.addWidget(QLabel('Select Asset:'))
        left_layout.addWidget(self.asset_selector)
        left_layout.addWidget(QLabel('Quantity (USD):'))
        left_layout.addWidget(self.quantity_input)
        left_layout.addWidget(QLabel('Fee Tier:'))
        left_layout.addWidget(self.fee_tier_input)
        left_layout.addWidget(self.start_button)

        # Right Panel - Output parameters
        right_layout = QVBoxLayout()
        self.label_slippage = QLabel('Slippage: Waiting...')
        self.label_fees = QLabel('Fees: Waiting...')
        self.label_impact = QLabel('Impact: Waiting...')
        self.label_net = QLabel('Net Cost: Waiting...')
        self.label_latency = QLabel('Latency: Waiting... ms')
        self.label_maker_taker = QLabel('Maker/Taker: Waiting...')

        right_layout.addWidget(self.label_slippage)
        right_layout.addWidget(self.label_fees)
        right_layout.addWidget(self.label_impact)
        right_layout.addWidget(self.label_net)
        right_layout.addWidget(self.label_latency)
        right_layout.addWidget(self.label_maker_taker)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        # Connect button to start WebSocket with input parameters
        self.start_button.clicked.connect(self.start_simulation)

    def start_simulation(self):
        asset = self.asset_selector.currentText()
        quantity = float(self.quantity_input.text())
        fee_tier = self.fee_tier_input.text()

        # Start websocket with parameters in a new thread so UI doesn't freeze
        threading.Thread(target=start_websocket, args=(self, asset, quantity, fee_tier), daemon=True).start()

    # Update UI labels with data from websocket
    def update_labels(self, slippage, fees, impact, net, latency_ms, maker_taker_prob):
        self.label_slippage.setText(f'Slippage: {slippage*100:.2f}%')
        self.label_fees.setText(f'Fees: {fees:.4f} USD')
        self.label_impact.setText(f'Impact: {impact*100:.2f}%')
        self.label_net.setText(f'Net Cost: {net*100:.2f}%')
        self.label_latency.setText(f'Latency: {latency_ms:.2f} ms')

        # Show maker/taker probability nicely
        if maker_taker_prob >= 0.5:
            label = f"Maker/Taker Probability: {(maker_taker_prob*100):.2f}% Taker"
        else:
            label = f"Maker/Taker Probability: {(100 - maker_taker_prob*100):.2f}% Maker"
        self.label_maker_taker.setText(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TradeSimulatorUI()
    window.show()
    sys.exit(app.exec_())
