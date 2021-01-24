from aqt import mw
from aqt.qt import *
from .ui import QHSeparationLine

class DlgConfig(QDialog):
    def __init__(self, config):
        super(DlgConfig, self).__init__(mw)
        self.setWindowTitle('Audio Files')
        self.setWindowFlags(Qt.Dialog)

        self._dir = QLineEdit()
        self._dir.setText(config['dir'] if 'dir' in config else '')
        self._dir.textChanged.connect(lambda v: self._setConfigValue(config, 'dir', v))
        self._dir.setToolTip('directory to copy sound data to')

        self._random = QComboBox()
        self._random.addItem('use field text', None)
        self._random.addItem('random', 'random')
        self._random.setCurrentIndex(1 if 'filenames' in config and config['filenames'].lower() == 'random' else 0)
        self._random.currentTextChanged.connect(lambda v: self._setConfigValue(config, 'filenames', v))

        self._use_selection = QCheckBox()
        self._use_selection.setText('search using selected text?')
        self._use_selection.setChecked(config['use_selection'] if 'use_selection' in config else False)
        self._use_selection.toggled.connect(lambda v: self._setConfigValue(config, 'use_selection', v))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QGridLayout()
        layout.addWidget(QLabel('Copy to: '), 0, 0)
        layout.addWidget(self._dir, 0, 1, 1, 2)
        layout.addWidget(QLabel('Filenames: '), 1, 0)
        layout.addWidget(self._random, 1, 1, 1, 2)
        layout.addWidget(self._use_selection, 2, 1, 1, 2)

        row = 3
        for name in config['sources']:
            row = self._addSourceConfig(layout, row, name, config['sources'][name])
        
        layout.addWidget(QHSeparationLine(), row, 0, 1, 3)
        layout.addWidget(buttonBox, row + 1, 0, 1, 3)
        self.setLayout(layout)

    def _addSourceConfig(self, layout, row, name, config):
        enabled = QCheckBox()
        enabled.setChecked(config['enabled'])
        enabled.toggled.connect(lambda v: self._setConfigValue(config, 'enabled', v))

        layout.addWidget(QHSeparationLine(), row, 0, 1, 3)
        row = row + 1
        layout.addWidget(QLabel(name), row, 0)
        layout.addWidget(QLabel('enabled?'), row, 1)
        layout.addWidget(enabled, row, 2)
        row = row + 1
        for key in config.keys():
            if key != 'enabled':
                attribute = QLineEdit()
                attribute.setText(config[key])
                attribute.textChanged.connect(lambda v: self._setConfigValue(config, key, v))

                layout.addWidget(QLabel(key), row, 1)
                layout.addWidget(attribute, row, 2)
                row = row + 1
        return row

    def _setConfigValue(self, config, key, value):
        config[key] = value
