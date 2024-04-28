CREATE DATABASE proyectouno;
USE proyectouno;
CREATE TABLE categoria(
	id_categoria INTEGER NOT NULL,
    nombre VARCHAR(25) NOT NULL
);
ALTER TABLE categoria ADD CONSTRAINT categoria_pk PRIMARY KEY (id_categoria);

CREATE TABLE pais(
	id_pais INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL
);
ALTER TABLE pais ADD CONSTRAINT pais_pk PRIMARY KEY (id_pais);

CREATE TABLE producto(
	id_producto INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    precio NUMERIC(6,2) NOT NULL,
    categoria_id_categoria INTEGER NOT NULL
);
ALTER TABLE producto ADD CONSTRAINT producto_pk PRIMARY KEY (id_producto);
ALTER TABLE producto ADD CONSTRAINT producto_categoria_fk FOREIGN KEY (categoria_id_categoria) REFERENCES categoria (id_categoria);


CREATE TABLE cliente(
	id_cliente INTEGER NOT NULL,
    nombre VARCHAR(15) NOT NULL,
    apellido VARCHAR(25) NOT NULL,
    direccion VARCHAR(100) NOT NULL,
    telefono VARCHAR(10) NOT NULL,
    tarjeta VARCHAR(20) NOT NULL,
    edad INTEGER NOT NULL,
    salario INTEGER NOT NULL,
    genero CHAR(1) NOT NULL,
    pais_id_pais INTEGER NOT NULL
);
ALTER TABLE cliente ADD CONSTRAINT cliente_pk PRIMARY KEY (id_cliente);
ALTER TABLE cliente ADD CONSTRAINT cliente_pais_fk FOREIGN KEY (pais_id_pais) REFERENCES pais (id_pais);

CREATE TABLE vendedor(
	id_vendedor INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    pais_id_pais INTEGER NOT NULL
);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_pk PRIMARY KEY (id_vendedor);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_pais_fk FOREIGN KEY (pais_id_pais) REFERENCES pais (id_pais);

CREATE TABLE orden(
	id_orden INTEGER AUTO_INCREMENT NOT NULL,
    linea_orden INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    vendedor_id_vendedor INTEGER NOT NULL,
    producto_id_producto INTEGER NOT NULL
);
ALTER TABLE orden ADD CONSTRAINT orden_pk PRIMARY KEY (id_orden);
ALTER TABLE orden ADD CONSTRAINT orden_compra_fk FOREIGN KEY (vendedor_id_vendedor) REFERENCES vendedor (id_vendedor);
ALTER TABLE orden ADD CONSTRAINT orden_producto_fk FOREIGN KEY (producto_id_producto) REFERENCES producto (id_producto);


CREATE TABLE detalle (
    id_detalle SERIAL PRIMARY KEY,
    fecha_orden VARCHAR(10) NOT NULL,
    cliente_id_cliente INTEGER NOT NULL,
    orden_id_orden INTEGER NOT NULL,
    CONSTRAINT unique_orden_cliente_fecha UNIQUE (orden_id_orden, fecha_orden, cliente_id_cliente)
);
ALTER TABLE detalle ADD CONSTRAINT detalle_pk PRIMARY KEY (id_detalle);
ALTER TABLE detalle ADD CONSTRAINT detalle_cliente_fk FOREIGN KEY (cliente_id_cliente) REFERENCES cliente (id_cliente);
ALTER TABLE detalle ADD CONSTRAINT detalle_orden_fk FOREIGN KEY (orden_id_orden) REFERENCES orden (id_orden);





