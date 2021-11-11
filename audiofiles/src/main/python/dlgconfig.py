from aqt import mw
from aqt.qt import *
from .ui import QHSeparationLine
from .rules import RULES

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
            if key != 'enabled' and key != 'rules':
                attribute = QLineEdit()
                attribute.setText(config[key])
                attribute.textChanged.connect(self._get_config_callback(config, key))
                layout.addWidget(QLabel(key), row, 1)
                layout.addWidget(attribute, row, 2)
                row = row + 1

        layout.addWidget(QLabel('search rules'), row, 1)
        layout.addWidget(self._getRulePanel(config), row, 2)
        row = row + 1

        return row

    def _getRulePanel(self, config):
        if 'rules' not in 'config':
            config['rules'] = ['lower case']

        layout = QGridLayout()
        row = 0
        for name in RULES.keys():
            rule = QCheckBox()
            rule.setChecked(name in config['rules'])
            rule.toggled.connect(self._get_config_rule_callback(config, name))
            layout.addWidget(rule, row, 0)
            layout.addWidget(QLabel(RULES[name]['description']), row, 1)
            row = row + 1
        panel = QWidget()
        panel.setLayout(layout)
        return panel

    def _get_config_callback(self, config, key):
        return lambda v: self._setConfigValue(config, key, v)

    def _setConfigValue(self, config, key, value):
        config[key] = value

    def _get_config_rule_callback(self, config, rule):
        return lambda v: self._setConfigRuleValue(config, rule, v)

    def _setConfigRuleValue(self, config, rule, selected):
        if 'rules' not in config:
            config['rules'] = []

        if selected:
            if rule not in config['rules']:
                config['rules'].append(rule)
        else:
            if rule in config['rules']:
                config['rules'].remove(rule)
        