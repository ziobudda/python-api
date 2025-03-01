# Modelli Pydantic

Pydantic è utilizzato per la validazione dei dati e la serializzazione/deserializzazione in questo progetto. Questa guida mostra come definire e utilizzare i modelli Pydantic seguendo le convenzioni del progetto.

## Definizione di Base dei Modelli

```python
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Modello per richieste in ingresso
class CreateItemRequest(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)  # Campo obbligatorio e maggiore di zero
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

# Modello per risposte
class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: str  # ISO 8601 format
```

## Tipi di Dati Comuni

```python
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date

class ExampleModel(BaseModel):
    # Tipi di base
    string_field: str
    int_field: int
    float_field: float
    bool_field: bool
    
    # Tipi opzionali
    optional_string: Optional[str] = None
    
    # Tipi con valore predefinito
    default_int: int = 0
    default_list: List[str] = []
    
    # Tipi complessi
    string_list: List[str]
    nested_dict: Dict[str, Any]
    string_to_int_map: Dict[str, int]
    
    # Tipi specializzati
    url_field: HttpUrl
    email_field: EmailStr  # Richiede pydantic[email]
    
    # Tipi temporali
    timestamp: datetime
    date_only: date
    
    # Campi con validazione
    positive_number: float = Field(..., gt=0)
    limited_string: str = Field(..., min_length=3, max_length=50)
    range_number: int = Field(..., ge=1, le=100)  # tra 1 e 100 inclusi
```

## Validatori Personalizzati

```python
from pydantic import BaseModel, validator

class UserModel(BaseModel):
    username: str
    password: str
    password_confirm: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('username deve contenere solo caratteri alfanumerici')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('le password non coincidono')
        return v
```

## Modelli Annidati

```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class User(BaseModel):
    name: str
    email: str
    addresses: List[Address]
    primary_address: Optional[Address] = None
```

## Conversione da/a Dizionari

```python
# Da dizionario a modello
user_data = {
    "name": "Mario Rossi",
    "email": "mario@example.com",
    "addresses": [
        {"street": "Via Roma 1", "city": "Milano", "country": "Italia", "postal_code": "20100"}
    ]
}
user = User(**user_data)

# Da modello a dizionario
user_dict = user.dict()

# Da modello a JSON
user_json = user.json()

# Esclusione di campi nulli
user_dict_no_nulls = user.dict(exclude_none=True)

# Inclusione solo di campi specifici
user_dict_partial = user.dict(include={"name", "email"})
```

## Best Practices per i Modelli

### 1. Separazione Request/Response

Separa sempre i modelli di richiesta e risposta, anche se simili:

```python
class ItemCreateRequest(BaseModel):
    name: str
    price: float

class ItemResponse(BaseModel):
    id: str
    name: str
    price: float
    created_at: str
```

### 2. Documentazione dei Campi

Usa `Field` con descrizioni per documentare i campi:

```python
class SearchQuery(BaseModel):
    query: str = Field(..., description="Testo da cercare")
    limit: int = Field(10, description="Numero massimo di risultati")
```

### 3. Validazione Coerente

Usa i validatori per garantire la coerenza dei dati:

```python
class DateRangeQuery(BaseModel):
    start_date: date
    end_date: date
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date deve essere successiva a start_date')
        return v
```

### 4. Modelli di Elenco

Per le risposte con elenchi di elementi, usa un modello contenitore:

```python
class ItemsList(BaseModel):
    items: List[ItemResponse]
    count: int
    total: int
    page: int
```

## Utilizzo nei Router

```python
@router.post("/items", response_model=Dict[str, Any])
async def create_item(
    item: ItemCreateRequest,
    token: str = token_dependency
):
    try:
        # Logica per creare l'elemento...
        
        # Conversione al modello di risposta
        result = ItemResponse(
            id="123",
            name=item.name,
            price=item.price,
            created_at=datetime.now().isoformat()
        )
        
        return success_response(
            data=result.dict(),
            message="Item creato con successo"
        )
    except Exception as e:
        return error_response(message=str(e))
```
