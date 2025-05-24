from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List
from database import Base

# Database Models
class Host(Base):
    __tablename__ = "hosts"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True)
    services = relationship("Service", back_populates="host", cascade="all, delete-orphan")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(Integer, ForeignKey("hosts.id"))
    port = Column(Integer)
    protocol = Column(String)
    host = relationship("Host", back_populates="services")

# Pydantic Models (Schemas)
class ServiceBase(BaseModel):
    port: int
    protocol: str

class ServiceCreate(ServiceBase):
    pass

class ServiceOut(ServiceBase):
    id: int
    host_id: int

    class Config:
        from_attributes = True

class HostBase(BaseModel):
    ip: str

class HostCreate(HostBase):
    services: List[ServiceCreate] = []

class HostUpdate(HostBase):
    pass

class HostOut(HostBase):
    id: int
    services: List[ServiceOut] = []

    class Config:
        from_attributes = True