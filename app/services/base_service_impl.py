from typing import Any, Dict
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

@as_declarative()
class Base:
    id: int
    __name__: str

    # Para que SQLAlchemy sepa que esta clase es la base de todas las tablas
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Método para convertir de schema a modelo
    def from_schema(self, schema):
        for field, value in schema.model_dump().items():
            setattr(self, field, value)

    # Método para obtener un dict con los campos del modelo (sin id)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != "id"}

    # Método para obtener el estado de la instancia (nuevo o modificado)
    def is_modified(self):
        return bool(self.id)  # Modificado si tiene id asignada

    # Método para guardar la instancia en la base de datos
    def save(self, db: Session):
        if not self.is_modified():
            db.add(self)  # Nuevo registro
        db.commit()
        db.refresh(self)  # Refrescar para obtener los valores actualizados (como el id)

    # Método para eliminar la instancia de la base de datos
    def delete(self, db: Session):
        db.delete(self)
        db.commit()

    # Método para cargar relaciones (eager loading)
    def load_relationships(self, db: Session, *relationships):
        for relationship in relationships:
            getattr(db.query(self.__class__).filter_by(id=self.id).options(selectinload(relationship)).first(), relationship)

    # Método para convertir a modelo SQLAlchemy (sin relaciones anidadas)
    def to_model(self, schema):
        """
        Convertir un schema Pydantic a kwargs para crear la instancia SQLAlchemy.
        Si hay objetos anidados (dict) que contienen 'id', se transforman a la clave FK '{key}_id'.
        Se ignoran otros objetos anidados para evitar pasar dicts directos al constructor SQLAlchemy.
        """
        model_class = self.model_class
        data = schema.model_dump(exclude_unset=True)

        processed = {}
        for key, value in data.items():
            # Si es un dict (objeto anidado), intentar extraer su id y mapear a FK
            if isinstance(value, dict):
                if 'id' in value and value['id'] is not None:
                    processed[f"{key}_id"] = value['id']
                # Si no tiene id, omitimos el campo para evitar pasar dicts a SQLAlchemy
                # (puedes extender aquí para crear/obtener la instancia relacionada si lo requieres)
                continue
            # Si es lista (relación varios), omitimos (manejar explícitamente si se desea)
            if isinstance(value, list):
                # Ignorar listas por defecto; relaciones tipo one-to-many deben manejarse aparte.
                continue
            # Campo simple: copiar tal cual
            processed[key] = value

        return model_class(**processed)

# Reemplazamos por una implementación simple y segura de BaseServiceImpl
class BaseServiceImpl:
	"""
	Servicio base para operaciones CRUD.
	- repository: debe exponer métodos save(instance), get(id), delete(id), list(...)
	- model_class: clase SQLAlchemy a instanciar
	"""

	def __init__(self, repository, model_class):
		self.repository = repository
		self.model_class = model_class

	def save(self, schema: Any):
		"""
		Convierte el schema a una instancia del modelo y delega al repositorio para persistir.
		El schema puede ser un Pydantic model (con model_dump) o un dict.
		"""
		model_instance = self.to_model(schema)
		return self.repository.save(model_instance)

	def to_model(self, schema: Any):
		"""
		Normaliza el payload antes de crear la instancia SQLAlchemy:
		- Si el campo es un dict y contiene 'id' -> lo convierte a '{key}_id'
		- Si el campo ya es '{key}_id' lo mantiene
		- Omite listas y dicts complejos sin id (no intentar crear relaciones automáticamente)
		"""
		# Obtener un dict plano desde Pydantic o dict ordinario
		if hasattr(schema, "model_dump"):
			data = schema.model_dump(exclude_unset=True)
		elif isinstance(schema, dict):
			data = dict(schema)
		else:
			# Intentar convertir atributos públicos
			data = {k: getattr(schema, k) for k in dir(schema) if not k.startswith("_") and not callable(getattr(schema, k))}

		processed: Dict[str, Any] = {}
		for key, value in data.items():
			# Mantener claves de FK ya formateadas
			if key.endswith("_id"):
				processed[key] = value
				continue

			# Si vienen objetos anidados: usar su id (si existe) como FK
			if isinstance(value, dict):
				if "id" in value and value["id"] is not None:
					processed[f"{key}_id"] = value["id"]
				# si no hay id, omitimos para evitar pasar dicts a SQLAlchemy
				continue

			# Omitir listas (relaciones one-to-many) por defecto
			if isinstance(value, list):
				continue

			# Campo simple -> mantener
			processed[key] = value

		# Crear la instancia del modelo con los campos procesados
		return self.model_class(**processed)

	# Métodos auxiliares comunes (opcionalmente usados por los servicios hijos)
	def get(self, id_):
		return self.repository.get(id_)

	def delete(self, id_):
		return self.repository.delete(id_)

	def list(self, *args, **kwargs):
		return self.repository.list(*args, **kwargs)