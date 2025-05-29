## Best Practices for Structured Outputs & Streaming Text with OpenAI Responses API

> **Objective:** Equip AI-driven applications with robust, real-time chat capabilities that emit both structured data and streaming text concurrently, ensuring predictable schema compliance and a smooth user experience.

---

### 1. JSON Schema Design & Injection

1. **Craft a Comprehensive JSON Schema**
    
    - Use JSON Schema Draft 2020‑12. Define `properties`, `required`, `type`, `pattern`, and `additionalProperties: false`.
        
    - Example schema for a weather report:
        
        ```json
        {
          "$schema": "http://json-schema.org/draft/2020-12/schema#",
          "type": "object",
          "properties": {
            "location": { "type": "string" },
            "temperature": { "type": "number" },
            "conditions": { "type": "string" }
          },
          "required": ["location","temperature","conditions"],
          "additionalProperties": false
        }
        ```
        
2. **Inject Schema in API Request**
    
    ```js
    const schema = /* as above */;
    const response = await client.responses.create({
      model: "gpt-4o",
      input: userPrompt,
      stream: true,
      json_schema: schema,
      strict: true
    });
    ```
    
    - `json_schema` ensures `response.output_json.delta` events conform.
        
    - `strict: true` rejects non-conforming tokens, prompting model corrections.
        
3. **Client-Side Validation**
    
    - Use validators like [AJV](https://ajv.js.org/) or Python’s `jsonschema.validate()` on each JSON delta chunk.
        
    - Merge fragments: accumulate partial objects, validate only when `response.output_json.delta` signals completion of that object.
        

---

### 2. Streaming & Semantic Event Handling

1. **Enable Streaming**
    
    ```python
    response_stream = client.responses.create(
      model="gpt-4o",
      input=user_prompt,
      stream=True,
      json_schema=schema,
      strict=True
    )
    ```
    
2. **Core Event Types**
    
    |Event Type|Purpose|
    |---|---|
    |`response.output_text.delta`|Text tokens for UI typing effect|
    |`response.output_json.delta`|Structured data fragments|
    |`tool.call` / `tool.response`|Function-calling lifecycle events|
    |`response.completed`|Signals full completion|
    
3. **Unified Event Loop (Python)**
    
    ```python
    from openai import OpenAI
    from jsonschema import validate, ValidationError
    
    client = OpenAI(api_key=API_KEY)
    schema_accumulator = ""
    structured_data = {}
    
    for evt in client.responses.create(..., stream=True):
        if evt.type == "response.output_text.delta":
            ui.append_text(evt.data.delta)
        elif evt.type == "response.output_json.delta":
            schema_accumulator += evt.data.delta
            try:
                obj = json.loads(schema_accumulator)
                validate(obj, schema)
                structured_data.update(obj)
                schema_accumulator = ""
                ui.update_structured_view(structured_data)
            except (json.JSONDecodeError, ValidationError):
                # wait for more fragments
                pass
        elif evt.type == "tool.call":
            handle_tool_call(evt.data)
        elif evt.type == "response.completed":
            ui.finalize()
    ```
    

---

### 3. Frontend Integration Patterns

#### 3.1 SSE (JavaScript)

```js
const es = new EventSource('/api/chat/stream');
es.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  switch(type) {
    case 'response.output_text.delta':
      chat.append(data.delta);
      break;
    case 'response.output_json.delta':
      jsonBuffer += data.delta;
      try { updateStructured(JSON.parse(jsonBuffer)); jsonBuffer = ''; }
      catch {};
      break;
    case 'response.completed':
      chat.markComplete();
      break;
  }
};
es.onerror = () => setTimeout(() => es = new EventSource(es.url), 1000);
```

#### 3.2 Fetch + ReadableStream (React)

```js
const [jsonBuffer, setJsonBuffer] = useState('');

useEffect(() => {
  fetch('/api/chat', { method: 'POST' }).then(res => {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    const read = async () => {
      const { done, value } = await reader.read();
      if (done) return;
      const chunk = decoder.decode(value, { stream: true });
      chunk.split(/\r?\n/).forEach(line => {
        if (!line) return;
        const { type, data } = JSON.parse(line);
        if (type === 'response.output_text.delta') appendText(data.delta);
        else if (type === 'response.output_json.delta') {
          setJsonBuffer(prev => prev + data.delta);
          try { updateStructured(JSON.parse(jsonBuffer)); setJsonBuffer(''); } catch {};
        }
      });
      read();
    };
    read();
  });
}, []);
```

---

### 4. Performance & Reliability Tips

- **Batch UI Updates:** Wrap text-appends in `requestAnimationFrame` to reduce reflows.
    
- **Exponential Backoff on Reconnects:** Implement `retryDelay = min(maxDelay, retryDelay * 2)`.
    
- **Timeout Handling:** Abort fetch after a threshold and fall back to non-streamed call.
    

---

### 5. Security & Sanitization

- **Escape HTML Entities:** Convert `<`, `>`, `&` in model outputs before injecting.
    
- **Use a Strict CSP:** `default-src 'self'; script-src 'none';` to mitigate XSS risks.
    

---

### 6. AI Implementation Notes

1. **Prompt Engineering:** Instruct the model to adhere strictly to the schema:
    
    ```text
    Please respond ONLY with JSON matching the provided schema. Do not wrap in markdown or add extra commentary.
    ```
    
2. **Error Recovery:** If the model returns invalid JSON, include a fallback prompt:
    
    ```text
    The last response was malformed. Please resend only the JSON object that matches the schema.
    ```
    
3. **Logging & Analytics:** Track event latency, number of deltas, and validation failures to tune model parameters.
    

---

_End of document._