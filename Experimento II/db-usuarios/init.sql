CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    acceso BOOLEAN NOT NULL DEFAULT false,
    pais_origen VARCHAR(255) NOT NULL
);

INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Juan Perez', true, 'CO' );
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Maria Garcia', false, 'MX');
INSERT INTO usuarios (nombre, acceso, pais_origen) VALUES ('Pedro Gomez', true, 'CO');
