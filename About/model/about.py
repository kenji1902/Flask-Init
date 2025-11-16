from MainApp.db import db

class about(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<About {self.id}>'
    
    def save(self, commit: bool = True):
        """Persist this model instance to the database.

        Args:
            commit: if True (default) commit the transaction. If False,
                    the instance is added to the session and flushed but
                    not committed (useful for batching multiple operations).

        Returns:
            self

        Raises:
            Exception: any exception raised by the database layer is
                       propagated after rolling back the session.
        """
        db.session.add(self)
        try:
            if commit:
                db.session.commit()
            else:
                # ensure the object has an id assigned (if using DB-side PK)
                db.session.flush()
            return self
        except Exception:
            db.session.rollback()
            raise

    def delete(self, commit: bool = True):
        """Remove this model instance from the database.

        Args:
            commit: if True commit the change immediately, otherwise leave
                    it to the caller to commit.
        """
        try:
            db.session.delete(self)
            if commit:
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise