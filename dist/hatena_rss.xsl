<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns="http://purl.org/rss/1.0/"
 xmlns:rss="http://purl.org/rss/1.0/"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#"
 xmlns:exsl="http://exslt.org/common"
 xmlns:func="http://exslt.org/functions"
 xmlns:my="urn:user-namespace-here"
 extension-element-prefixes="exsl func my"
 exclude-result-prefixes="rss hatena">
<xsl:output method="xml" encoding="UTF-8" indent="yes"/>

<xsl:variable name="tmp">
 <xsl:for-each select="//rss:item">
  <xsl:sort select="dc:date"/>
  <pt about="{@rdf:about}" date="{dc:date}">
   <xsl:value-of select="concat(
    'http://a.st-hatena.com/go?',
    @rdf:about,
    translate(substring-before(dc:date,'+'),'-T:','')
   )"/>
  </pt>
 </xsl:for-each>
</xsl:variable>
<xsl:variable name="pts" select="exsl:node-set($tmp)"/>

<func:function name="my:url">
 <xsl:param name="u"/>
 <func:result>
  <xsl:value-of select="$pts/rss:pt[@about=$u]"/>
 </func:result>
</func:function>

<xsl:template match="rss:channel">
 <channel rdf:about="{@rdf:about}">
  <title><xsl:value-of select="rss:title"/></title>
  <link><xsl:value-of select="rss:link"/></link>
  <description><xsl:value-of select="rss:description"/></description>
  <dc:date><xsl:value-of select="$pts/rss:pt[last()]/@date"/></dc:date>
  <xsl:apply-templates select="rss:items"/>
 </channel>
</xsl:template>

<xsl:template match="rss:items">
 <items>
  <xsl:apply-templates select="rdf:Seq"/>
 </items>
</xsl:template>

<xsl:template match="rdf:Seq">
 <rdf:Seq>
  <xsl:for-each select="rdf:li">
   <rdf:li rdf:resource="{my:url(@rdf:resource)}"/>
  </xsl:for-each>
 </rdf:Seq>
</xsl:template>

<xsl:template match="rdf:RDF">
 <rdf:RDF xmlns="http://purl.org/rss/1.0/">
  <xsl:apply-templates select="rss:channel"/>
  <xsl:for-each select="rss:item">
   <item rdf:about="{my:url(@rdf:about)}">
    <title><xsl:value-of select="rss:title"/></title>
    <link><xsl:value-of select="my:url(rss:link)"/></link>
    <description><xsl:value-of select="normalize-space(rss:description)"/></description>
    <dc:data><xsl:value-of select="dc:date"/></dc:data>
   </item>
  </xsl:for-each>
 </rdf:RDF>
</xsl:template>

</xsl:stylesheet>
