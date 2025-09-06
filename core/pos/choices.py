GENDER = (
    ('male','Masculino'),
    ('female','Femenino'),
)

PAYMENTMETHODS = (
    ('cash', 'Efectivo'),
    ('creditCard', 'Tarjeta Crédito'),
    ('debitCard', 'Tarjeta Débito'),
    ('transfer', 'Transferencia'),
    ('mixto', 'Mixto'),
)

TYPETMETHODS = (
    ('fullpayment', 'Contado'),
    ('credit', 'Crédito'),
)

TRANSFERMETHODS = (
    ('nequi', 'Nequi'),
    ('daviplata', 'Daviplata'),
    ('mixto1', 'Nequi + Efectivo'),
    ('mixto2', 'Daviplata + Efectivo'),
    ('mixto3', 'Nequi + daviplata'),
)

EXPENSES = (
    ('caja', 'Caja'),
    ('general', 'General'),
)

SERVICE_TYPE = (
    ('in_site', 'En Sitio'),
    ('delivery', 'Domicilio'),
)