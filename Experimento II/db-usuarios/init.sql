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
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Carlos Rodriguez', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Ana Martinez', true, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Luis Hernandez', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Carmen Lopez', true, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Diego Sanchez', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Sofia Ramirez', true, 'AR');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Andres Torres', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Valentina Flores', true, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Sebastian Castro', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Isabella Morales', true, 'PE');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Nicolas Vargas', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Camila Gutierrez', true, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Mateo Jimenez', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Valeria Ruiz', true, 'CL');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Samuel Diaz', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Daniela Herrera', true, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Alejandro Moreno', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Gabriela Silva', true, 'UY');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('David Rojas', true, 'CO');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Natalia Vega', true, 'MX');