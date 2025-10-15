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

TIPO_CONTRATO = [
        ('F', 'Término Fijo'),
        ('I', 'Término Indefinido'),
        ('O', 'Obra o labor'),
        ('P', 'Prestación de servicios'),
    ]

PERIODO_NOMINA = [
        ('Q1', 'Primera quincena'),
        ('Q2', 'Segunda quincena'),
        ('M', 'Mensual'),
    ]