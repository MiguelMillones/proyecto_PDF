"""
Manejo de progreso para operaciones largas
Soporta múltiples backends y threading
"""
from typing import Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject
import time


class WorkerSignals(QObject):
    """Señales para comunicación entre threads"""
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(object)  # resultado
    error = pyqtSignal(str)  # mensaje de error


class PDFWorker(QThread):
    """Thread worker para operaciones PDF sin bloquear la UI"""
    
    def __init__(self, task_func, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    def run(self):
        """Ejecutar la tarea en segundo plano"""
        try:
            # Configurar callback de progreso
            def progress_callback(current, total, message=""):
                self.signals.progress.emit(current, total, message)
            
            # Ejecutar la tarea con callback
            result = self.task_func(
                *self.args,
                callback_progreso=progress_callback,
                **self.kwargs
            )
            self.signals.finished.emit(result)
            
        except Exception as e:
            self.signals.error.emit(str(e))


class ProgressBarManager:
    """Manejador de barra de progreso para la UI"""
    
    def __init__(self, progress_bar, label=None):
        self.progress_bar = progress_bar
        self.label = label
        self.current_worker = None
        
    def start_operation(self, task_func, *args, on_finished=None, on_error=None, **kwargs):
        """Iniciar una operación con barra de progreso"""
        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        if self.label:
            self.label.setVisible(True)
            self.label.setText("Iniciando...")
        
        # Crear y configurar worker
        self.current_worker = PDFWorker(task_func, *args, **kwargs)
        self.current_worker.signals.progress.connect(self.update_progress)
        
        if on_finished:
            self.current_worker.signals.finished.connect(on_finished)
        if on_error:
            self.current_worker.signals.error.connect(on_error)
            
        # Conectar limpieza automática
        self.current_worker.signals.finished.connect(self._on_operation_finished)
        self.current_worker.signals.error.connect(self._on_operation_finished)
        
        # Iniciar worker
        self.current_worker.start()
        
    def update_progress(self, current, total, message):
        """Actualizar barra de progreso"""
        if total > 0:
            percentage = int((current / total) * 100)
            self.progress_bar.setValue(percentage)
            self.progress_bar.setFormat(f"{percentage}% - {current}/{total}")
        
        if self.label and message:
            self.label.setText(message)
            
    def _on_operation_finished(self, *args):
        """Limpiar después de finalizar"""
        self.current_worker = None
        # No ocultar inmediatamente para que el usuario vea el 100%
        
    def reset(self):
        """Resetear barra de progreso"""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("")
        self.progress_bar.setVisible(False)
        if self.label:
            self.label.setText("")
            self.label.setVisible(False)