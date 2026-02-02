-- 1. Crear la tabla de Logs (Solo lectura para la APP)
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    action VARCHAR(10), -- INSERT, UPDATE, DELETE
    record_id TEXT,     -- ID del registro afectado
    old_data TEXT,      -- Datos antes del cambio (JSON)
    new_data TEXT,      -- Datos nuevos (JSON)
    changed_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'America/Bogota'),
    app_user VARCHAR(100),  -- Usuario de la APP que hizo el cambio
    db_user VARCHAR(50) DEFAULT current_user -- Usuario de BD (postgres)
);

-- 2. Función Maestra que ejecuta el Trigger
CREATE OR REPLACE FUNCTION log_changes_trigger()
RETURNS TRIGGER AS $$
DECLARE
    current_app_user TEXT;
BEGIN

    current_app_user := current_setting('app.current_user', true);

    IF current_app_user IS NULL THEN
        current_app_user := 'System/DBUser';
    END IF;

    IF (TG_OP = 'INSERT') THEN
        INSERT INTO system_logs (table_name, action, record_id, new_data, app_user)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id_aud::TEXT, row_to_json(NEW)::TEXT, current_app_user);
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO system_logs (table_name, action, record_id, old_data, new_data, app_user)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id_aud::TEXT, row_to_json(OLD)::TEXT, row_to_json(NEW)::TEXT, current_app_user);
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO system_logs (table_name, action, record_id, old_data, app_user)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id_aud::TEXT, row_to_json(OLD)::TEXT, current_app_user);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- NOTA: Como tus tablas tienen IDs con nombres diferentes (id_aud, id_op, aud_user),
-- haremos triggers específicos pequeños para mapear el ID correctamente.

-- 3. Trigger para AUDITORIA
CREATE OR REPLACE FUNCTION log_auditoria() RETURNS TRIGGER AS $$
DECLARE
    current_app_user TEXT;
BEGIN

    current_app_user := current_setting('app.current_user', true);

    IF current_app_user IS NULL THEN
        current_app_user := 'System/DBUser';
    END IF;
    IF (TG_OP = 'INSERT') THEN INSERT INTO system_logs (table_name, action, record_id, new_data, app_user) VALUES ('auditoria', 'INSERT', NEW.id_aud, row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, new_data, app_user) VALUES ('auditoria', 'UPDATE', NEW.id_aud, row_to_json(OLD), row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, app_user) VALUES ('auditoria', 'DELETE', OLD.id_aud, row_to_json(OLD), current_app_user); RETURN OLD;
    END IF;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER t_audit_auditoria AFTER INSERT OR UPDATE OR DELETE ON auditoria
FOR EACH ROW EXECUTE FUNCTION log_auditoria();

-- 4. Trigger para AUDITOR (CRUD de usuarios)
CREATE OR REPLACE FUNCTION log_auditor() RETURNS TRIGGER AS $$
DECLARE
    current_app_user TEXT;
BEGIN

    current_app_user := current_setting('app.current_user', true);

    IF current_app_user IS NULL THEN
        current_app_user := 'System/DBUser';
    END IF;
    IF (TG_OP = 'INSERT') THEN INSERT INTO system_logs (table_name, action, record_id, new_data, app_user) VALUES ('auditor', 'INSERT', NEW.aud_user, row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, new_data, app_user) VALUES ('auditor', 'UPDATE', NEW.aud_user, row_to_json(OLD), row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, app_user) VALUES ('auditor', 'DELETE', OLD.aud_user, row_to_json(OLD), current_app_user); RETURN OLD;
    END IF;
    RETURN NULL;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER t_audit_auditor AFTER INSERT OR DELETE ON auditor
FOR EACH ROW EXECUTE FUNCTION log_auditor();

-- 5. Trigger para OPORTUNIDAD_MEJORA
CREATE OR REPLACE FUNCTION log_op_mejora() RETURNS TRIGGER AS $$
DECLARE
    current_app_user TEXT;
BEGIN
    current_app_user := current_setting('app.current_user', true);

    IF current_app_user IS NULL THEN
        current_app_user := 'System/DBUser';
    END IF;
    IF (TG_OP = 'INSERT') THEN INSERT INTO system_logs (table_name, action, record_id, new_data, app_user) VALUES ('op_mejora', 'INSERT', NEW.id_op::TEXT, row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, new_data, app_user) VALUES ('op_mejora', 'UPDATE', NEW.id_op::TEXT, row_to_json(OLD), row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, app_user) VALUES ('op_mejora', 'DELETE', OLD.id_op::TEXT, row_to_json(OLD), current_app_user); RETURN OLD;
    END IF;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER t_audit_op_mejora AFTER INSERT OR UPDATE OR DELETE ON op_mejora
FOR EACH ROW EXECUTE FUNCTION log_op_mejora();

-- 6. Trigger para COMPROMISOS 
CREATE OR REPLACE FUNCTION log_compromiso() RETURNS TRIGGER AS $$
DECLARE
    current_app_user TEXT;
BEGIN
    current_app_user := current_setting('app.current_user', true);

    IF current_app_user IS NULL THEN
        current_app_user := 'System/DBUser';
    END IF;
    IF (TG_OP = 'INSERT') THEN INSERT INTO system_logs (table_name, action, record_id, new_data, app_user) VALUES ('compromiso', 'INSERT', NEW.id_com::TEXT, row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, new_data, app_user) VALUES ('compromiso', 'UPDATE', NEW.id_com::TEXT, row_to_json(OLD), row_to_json(NEW), current_app_user); RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN INSERT INTO system_logs (table_name, action, record_id, old_data, app_user) VALUES ('compromiso', 'DELETE', OLD.id_com::TEXT, row_to_json(OLD), current_app_user); RETURN OLD;
    END IF;
END; $$ LANGUAGE plpgsql;

CREATE TRIGGER t_audit_compromiso AFTER INSERT OR UPDATE OR DELETE ON compromiso
FOR EACH ROW EXECUTE FUNCTION log_compromiso();