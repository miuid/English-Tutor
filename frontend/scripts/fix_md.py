import os

p = os.path.join(os.getcwd(), "src", "components", "ChatView.tsx")
with open(p, "r", encoding="utf-8") as f:
    t = f.read()

old = '                <p className="bubble-text">{turn.text}</p>'
new = '                <Markdown text={turn.text} className="bubble-text" />'

if old not in t:
    print("ERROR: old not found")
    # Show context around bubble-text
    idx = t.find('bubble-text')
    if idx >= 0:
        print(f"Context: {repr(t[idx-20:idx+60])}")
    exit(1)

t = t.replace(old, new)
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(t)
print("done")
