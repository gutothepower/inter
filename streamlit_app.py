
import streamlit as st
from firebase_admin import credentials, initialize_app, storage, firestore
import firebase_admin
import uuid
import datetime

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("inter-app-5ea72-firebase-adminsdk-fbsvc-547f9b6c8c.json")
    initialize_app(cred, {
        'storageBucket': 'inter-app-5ea72.appspot.com'
    })

db = firestore.client()
bucket = storage.bucket()

st.set_page_config(page_title="MerchTrack", layout="centered")
st.title("📦 Merchandise Received")

menu = ["Upload", "Dashboard"]
choice = st.sidebar.selectbox("Navigate", menu)

if choice == "Upload":
    st.subheader("📤 Upload Document")

    note = st.text_input("Optional Note (e.g., Supplier, Invoice)")
    uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        if st.button("Submit"):
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            filename = f"photos/{unique_id}.jpg"

            # Upload to Firebase Storage
            blob = bucket.blob(filename)
            blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
            blob.make_public()

            # Save metadata to Firestore
            db.collection("merch_submissions").add({
                "timestamp": datetime.datetime.now().isoformat(),
                "note": note,
                "photo_url": blob.public_url,
                "category": "Merchandise Received"
            })

            st.success("✅ Photo uploaded successfully!")

elif choice == "Dashboard":
    st.subheader("📊 Dashboard")
    docs = db.collection("merch_submissions").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

    for doc in docs:
        entry = doc.to_dict()
        st.markdown(f"**Date/Time:** {entry['timestamp']}")
        st.markdown(f"**Note:** {entry.get('note', '—')}")
        st.image(entry['photo_url'], width=300)
        st.markdown("---")
