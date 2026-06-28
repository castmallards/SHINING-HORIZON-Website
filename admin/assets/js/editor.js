// Rich-text editor wrapper around Quill (Phase 4.5).
// Pages include Quill via CDN in their <head>; this module mounts the
// editor onto a container and syncs it to a hidden textarea.

(function () {
    const REGISTRY = new Map(); // textareaId -> Quill instance

    function mount({ textareaId, containerId, placeholder = 'Write here...' }) {
        if (typeof Quill === 'undefined') {
            console.warn('Quill is not loaded — falling back to plain textarea.');
            return null;
        }
        const textarea = document.getElementById(textareaId);
        const container = document.getElementById(containerId);
        if (!textarea || !container) return null;

        // Hide the original textarea but keep it in the form so getFormData picks it up.
        textarea.style.display = 'none';

        container.innerHTML = '';
        const editor = new Quill(container, {
            theme: 'snow',
            placeholder,
            modules: {
                toolbar: [
                    [{ header: [2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ list: 'ordered' }, { list: 'bullet' }],
                    ['link', 'blockquote', 'code-block'],
                    ['clean'],
                ],
            },
        });

        if (textarea.value) editor.root.innerHTML = textarea.value;

        editor.on('text-change', () => {
            // Quill uses '<p><br></p>' to represent an empty doc; persist '' for that.
            const html = editor.root.innerHTML;
            textarea.value = html === '<p><br></p>' ? '' : html;
        });

        REGISTRY.set(textareaId, editor);
        return editor;
    }

    function setValue(textareaId, html) {
        const editor = REGISTRY.get(textareaId);
        if (editor) editor.root.innerHTML = html || '';
        const textarea = document.getElementById(textareaId);
        if (textarea) textarea.value = html || '';
    }

    function destroy(textareaId) {
        REGISTRY.delete(textareaId);
    }

    function sanitizeHtml(html) {
        if (typeof sanitizeRichHtml === 'function') return sanitizeRichHtml(html);
        return html || '';
    }

    window.RichEditor = { mount, setValue, destroy, sanitizeHtml };
})();
