"""
 deleage classes
"""

# pylint: disable=unused-argument, bad-continuation

from PySide2.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionButton,
    QApplication,
    QStyle,
    QComboBox,
)
from PySide2.QtCore import Qt, QRect, QPoint, QEvent, Slot


from ..jobs import JobStatus


class FillColorDelegate(QStyledItemDelegate):
    """FillColorDelegate
    """

    def __init__(self, model, color):
        """
        This delegate replaces a cell's display with a solid fill color
        surrounded by a thin white border

        :param model: underlying ProxyModel object
        :param color: QColor object
        """

        super().__init__()
        self.color = color
        self.model = model

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):

        source_index = self.model.mapToSource(index)
        row = source_index.row()
        column = source_index.column()
        value = self.model.sourceModel().dataset[row][column]
        rect = QRect(
            option.rect.x() + 1,
            option.rect.y() + 1,
            option.rect.width() - 2,
            option.rect.height() - 2,
        )

        if value:
            painter.save()
            painter.setBrush(self.color)
            painter.fillRect(rect, painter.brush())


class CheckBoxDelegate(QStyledItemDelegate):
    """ CheckBoxDelegate """

    def __init__(self, proxy_model):
        """
        This delegate replaces a cell's display with a check box. Underlying
        data are updated when the box is checked or unchecked. Persistant editor
        needs to be set on the table's cells in order to update the box.

        :param model: underlying ProxyModel object
        """

        self.proxy_model = proxy_model
        super().__init__()

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):

        # Check data
        source_index = self.proxy_model.mapToSource(index)
        row = source_index.row()
        column = source_index.column()
        checked = self.proxy_model.sourceModel().dataset[row][column]

        # Build rect to draw
        style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(
            QStyle.SE_CheckBoxIndicator, style_option, None
        )
        check_box_pos = QPoint(
            option.rect.x() + option.rect.width() / 2 - check_box_rect.width() / 2,
            option.rect.y() + option.rect.height() / 2 - check_box_rect.height() / 2,
        )
        rect_to_draw = QRect(check_box_pos, check_box_rect.size())

        # Build check box
        opts = QStyleOptionButton()
        opts.state |= QStyle.State_Active | QStyle.State_Enabled
        opts.state |= QStyle.State_On if checked else QStyle.State_Off
        opts.rect = rect_to_draw
        QApplication.style().drawControl(QStyle.CE_CheckBox, opts, painter)

    def editorEvent(self, event, model, option, index):

        source_index = model.mapToSource(index)
        column = source_index.column()
        if column and event.type() == QEvent.MouseButtonRelease:
            self.setModelData(None, model.sourceModel(), source_index)
            return True
        return False

    def setModelData(self, editor, model, index):

        row = index.row()
        column = index.column()
        model.dataset[row][column] = not model.dataset[row][column]


class StatusComboBoxDelegate(QStyledItemDelegate):
    """
    ComboBoxDelegate [summary]

    Args:
        QStyledItemDelegate ([type]): [description]

    Returns:
        [type]: [description]
    """

    comboItems = ["Wait", "Wait..", "Wait..."]

    def __init__(self, model):
        super(StatusComboBoxDelegate, self).__init__()

        self.model = model

    def createEditor(self, parent, option, index):

        sourceIndex = self.model.mapToSource(index)
        row = sourceIndex.row()
        column = sourceIndex.column()
        status = self.model.sourceModel().dataset[row, column]
        self.comboItems = _comboBoxItems(status)

        if self.comboItems:
            editor = QComboBox(parent)
            editor.addItems(self.comboItems)
            editor.currentIndexChanged.connect(self.currentIndexChanged)
            editor.setEditable(True)
            editor.lineEdit().setReadOnly(True)
            editor.lineEdit().setAlignment(Qt.AlignCenter)

            return editor

        return None

    def editorEvent(self, event, model, option, index):

        sourceIndex = model.mapToSource(index)
        column = sourceIndex.column()

        if column and event.type() == QEvent.MouseButtonRelease:
            self.setModelData(None, model.sourceModel(), sourceIndex)

            return False

        # if column and (event.type() == QEvent.KeyPress):
        #    if event.key() in [Qt.Key_Enter, Qt.Key_Return]:
        #        self.setModelData(None, model.sourceModel(), sourceIndex)
        #        return True

        return False

    def setModelData(self, editor, model, index):

        if editor:
            comboIndex = editor.currentIndex()
            text = self.comboItems[comboIndex]
            model.setData(index, text)

    @Slot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())


def _comboBoxItems(status):

    if status in [JobStatus.AbortJobError, JobStatus.Error]:
        return None

    elif status in [
        JobStatus.Skip,
        JobStatus.Skipped,
        JobStatus.Abort,
        JobStatus.Aborted,
        JobStatus.Done,
    ]:
        comboItems = [status, JobStatus.Waiting]

    elif status in [JobStatus.Queue, JobStatus.Waiting]:
        comboItems = [status, JobStatus.Skip]

    elif status in JobStatus.Running:
        comboItems = [status, JobStatus.Abort]

    else:
        return None

    return comboItems


class ComboBoxDelegateNew(QStyledItemDelegate):
    """
    ComboBoxDelegate [summary]

    Args:
        QStyledItemDelegate ([type]): [description]

    Returns:
        [type]: [description]
    """

    comboItems = ["Wait", "Wait..", "Wait..."]

    def __init__(self, proxyModel):

        self.proxyModel = proxyModel
        super().__init__()

    def createEditor(self, parent, option, proxyModelIndex):

        editor = QComboBox(self)
        editor.addItems(self.comboItems)
        editor.currentIndexChanged.connect(self.currentIndexChanged)

        return editor

    def editorEvent(self, event, model, option, index):
        source_index = model.mapToSource(index)
        column = source_index.column()
        if column and event.type() == QEvent.MouseButtonRelease:
            self.setModelData(None, model.sourceModel(), source_index)
            return True
        return False

    def setModelData(self, editor, model, index):

        row = index.row()
        column = index.column()
        model.dataset[row][column] = not model.dataset[row][column]

    @Slot()
    def currentIndexChanged(self):
        self.commitData.emit(self.sender())
