CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    acceso BOOLEAN NOT NULL DEFAULT true,
    pais_origen VARCHAR(255) NOT NULL
);

-- Registros con 70% de Colombia (70 registros) y 30% otros países (30 registros)
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Juan Perez', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Maria Garcia', true, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Pedro Gomez', true, 'CO');
