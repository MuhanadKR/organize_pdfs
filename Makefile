.PHONY: build install clean

build:
	# Create the Debian package
	dpkg-deb --build organize_pdfs

install:
	# Install the Debian package
	sudo dpkg -i organize_pdfs.deb

clean:
	# Remove build artifacts
	rm -rf organize_pdfs.deb
